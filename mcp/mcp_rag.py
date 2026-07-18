import json
import logging
import os
import sys
import urllib.request
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from rag_pipeline_faiss import INDEX_FILE, ask, ingest, iter_documents, load_index, retrieve
from app.rag.voice import dedupe_voice_sources, sanitize_voice_answer


if sys.platform == "win32":
    sys.stderr.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")


load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RAG_MCP")

mcp = FastMCP("LocalRAG")

DAC_API = os.getenv("DAC_API", "https://donganhcapital.onrender.com/api")
DAC_TIMEOUT = 12  # giây; Render free có thể ngủ (cold start ~60s) — không đợi lâu để robot không bị treo
DAC_OFFLINE_MSG = (
    "Máy chủ Đông Anh Capital đang khởi động lại, chưa có dữ liệu ngay. "
    "Bạn có thể xem trực tiếp tại Đông Anh Capital chấm com hoặc hỏi lại sau một phút."
)
DAC_STALE_PREFIX = "Máy chủ Đông Anh Capital đang khởi động lại. Số liệu phiên gần nhất mình có: "
DAC_CACHE_FILE = Path(__file__).resolve().parent / ".dac_cache.json"
DAC_CACHE_VERSION = 2

# Cache kết quả đã format của các tool dac_* (chuỗi chứa sẵn ngày phiên nên tự mô tả được).
# Giữ cả bản trên đĩa để sống sót qua restart process.
_dac_cache: dict = {}


def _voice_output(text: str) -> str:
    """Final plain-text gate for every answer that XiaoZhi may speak."""
    return dedupe_voice_sources(sanitize_voice_answer(text))


def _dac_cache_load() -> None:
    global _dac_cache
    try:
        payload = json.loads(DAC_CACHE_FILE.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("version") != DAC_CACHE_VERSION:
            raise ValueError("DAC cache is missing the current voice-text version")
        raw_cache = payload.get("responses")
        if not isinstance(raw_cache, dict):
            raise ValueError("DAC cache responses must be a JSON object")
        _dac_cache = {
            str(tool): _voice_output(text)
            for tool, text in raw_cache.items()
            if isinstance(text, str)
        }
    except Exception:
        _dac_cache = {}


def _dac_cache_put(tool: str, text: str) -> None:
    _dac_cache[tool] = _voice_output(text)
    try:
        payload = {"version": DAC_CACHE_VERSION, "responses": _dac_cache}
        DAC_CACHE_FILE.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    except OSError as exc:
        logger.warning("Không ghi được DAC cache: %s", exc)


def _dac_cache_get(tool: str):
    cached = _dac_cache.get(tool)
    return _voice_output(cached) if isinstance(cached, str) else None


_dac_cache_load()


def _dac_get(path: str):
    """GET một endpoint public của donganhcapital.com, trả về JSON đã parse."""
    url = f"{DAC_API}{path}"
    request = urllib.request.Request(url, headers={"User-Agent": "LilyRobot/1.0"})
    with urllib.request.urlopen(request, timeout=DAC_TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def _dac_fallback(tool: str) -> str:
    """Câu trả lời khi API DAC không phản hồi: ưu tiên số liệu cache gần nhất."""
    cached = _dac_cache_get(tool)
    if cached:
        return _voice_output(DAC_STALE_PREFIX + cached)
    return _voice_output(DAC_OFFLINE_MSG)


# Backend web Lily (cùng máy): bộ não RAG mạnh hơn (ChromaDB + e5 + Groq 70B)
# với persona giọng nói riêng. Nếu backend tắt thì rag_answer tự fallback FAISS.
WEB_BACKEND = os.getenv("LILY_WEB_BACKEND", "http://127.0.0.1:8000")
WEB_PROBE_TIMEOUT = 2    # giây — chỉ để biết backend có bật không
WEB_ANSWER_TIMEOUT = 45  # giây — retrieval + LLM cần thời gian thật


def _ask_web_backend(question: str):
    """Trả về câu trả lời từ backend web local, hoặc None để caller fallback FAISS."""
    try:
        probe = urllib.request.Request(f"{WEB_BACKEND}/health")
        with urllib.request.urlopen(probe, timeout=WEB_PROBE_TIMEOUT):
            pass
        payload = json.dumps({"message": question}).encode("utf-8")
        request = urllib.request.Request(
            f"{WEB_BACKEND}/chat/robot",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=WEB_ANSWER_TIMEOUT) as response:
            answer = json.loads(response.read().decode("utf-8")).get("answer", "").strip()
            return answer or None
    except Exception as exc:
        logger.warning("Web backend unavailable, falling back to FAISS: %s", exc)
        return None


@mcp.tool()
def rag_search(question: str, top_k: int = 4) -> str:
    """Tìm các đoạn liên quan trong kho tài liệu local."""
    try:
        contexts = retrieve(question, top_k=top_k)
    except Exception as exc:
        logger.exception("RAG search failed")
        return f"Lỗi khi tìm kiếm RAG: {exc}"

    logger.info("RAG search: %s | results=%s", question, len(contexts))
    if not contexts:
        return "Không tìm thấy đoạn nào liên quan trong kho tài liệu local."

    lines = ["Kết quả tìm kiếm RAG:"]
    for idx, (chunk, score) in enumerate(contexts, start=1):
        lines.append(
            f"\n{idx}. Nguồn: {chunk.source}\n"
            f"Độ liên quan: {score:.3f}\n"
            f"Nội dung: {chunk.text}"
        )
    return "\n".join(lines)


@mcp.tool()
def rag_answer(question: str, top_k: int = 4) -> str:
    """Trả lời câu hỏi từ kho tri thức cho robot; giữ nguyên câu trả lời khi đọc thành tiếng và luôn đọc tên thương hiệu là Đông Anh Capital."""
    answer = _ask_web_backend(question)
    if answer:
        logger.info("RAG answer (web backend): %s", question)
        return _voice_output(answer)

    try:
        answer = ask(question, top_k=top_k)
    except Exception as exc:
        logger.exception("RAG answer failed")
        return _voice_output(f"Lỗi khi trả lời RAG: {exc}")

    logger.info("RAG answer (FAISS): %s", question)
    return _voice_output(answer)


@mcp.tool()
def rag_reindex() -> str:
    """Tạo lại FAISS index từ các file trong thư mục data."""
    try:
        ingest()
    except Exception as exc:
        logger.exception("RAG reindex failed")
        return f"Lỗi khi tạo lại index RAG: {exc}"

    logger.info("RAG index rebuilt")
    return "Đã tạo lại FAISS index từ thư mục data/."


@mcp.tool()
def rag_status() -> str:
    """Kiểm tra tài liệu và FAISS index hiện có của RAG local."""
    documents = iter_documents()
    lines = [
        "Trạng thái RAG local:",
        f"- Số file tài liệu trong data/: {len(documents)}",
        f"- FAISS index tồn tại: {'có' if INDEX_FILE.exists() else 'không'}",
    ]

    for path in documents[:20]:
        lines.append(f"- Tài liệu: {path.name}")

    if INDEX_FILE.exists():
        try:
            index = load_index()
            lines.append(f"- Số chunk trong index: {len(index.get('chunks', []))}")
        except Exception as exc:
            lines.append(f"- Không đọc được index: {exc}")

    return "\n".join(lines)


@mcp.tool()
def dac_vnindex() -> str:
    """Lấy chỉ số VNINDEX mới nhất từ Đông Anh Capital. Dùng khi người dùng hỏi VNINDEX hôm nay thế nào hoặc thị trường chứng khoán Việt Nam ra sao. Kết quả đã là câu hoàn chỉnh cho TTS; giữ nguyên khi đọc."""
    try:
        rows = _dac_get("/vnindex?limit=2")
    except Exception as exc:
        logger.warning("dac_vnindex failed: %s", exc)
        return _dac_fallback("dac_vnindex")

    if not rows:
        return _voice_output("Chưa có dữ liệu VNINDEX.")

    latest = rows[-1]
    close = latest["Close"]
    date = str(latest["Date"])[:10]
    line = f"VNINDEX phiên {date}: đóng cửa {close:,.2f} điểm"
    if len(rows) >= 2:
        prev_close = rows[-2]["Close"]
        change = close - prev_close
        pct = change / prev_close * 100 if prev_close else 0
        direction = "tăng" if change >= 0 else "giảm"
        line += f", {direction} {abs(change):,.2f} điểm ({pct:+.2f}%) so với phiên trước"
    volume = latest.get("Volume")
    if volume:
        line += f". Khối lượng {volume / 1_000_000:,.0f} triệu đơn vị."
    line = _voice_output(line)
    _dac_cache_put("dac_vnindex", line)
    return line


@mcp.tool()
def dac_ai_signals_today() -> str:
    """Lấy tín hiệu AI breakout mới nhất từ Đông Anh Capital. Dùng khi người dùng hỏi hôm nay AI có tín hiệu hoặc gợi ý cổ phiếu nào. Kết quả đã là câu hoàn chỉnh cho TTS; giữ nguyên khi đọc."""
    try:
        summary = _dac_get("/ai-signals/summary")
    except Exception as exc:
        logger.warning("dac_ai_signals_today failed: %s", exc)
        return _dac_fallback("dac_ai_signals_today")

    latest_active = next((row for row in summary if row.get("signal_count", 0) > 0), None)
    if latest_active is None:
        return _voice_output(
            "Gần đây mô hình AI của Đông Anh Capital chưa phát tín hiệu breakout nào — "
            "mô hình rất chọn lọc, chỉ báo khi xác suất đủ tốt."
        )

    date = latest_active["date"]
    try:
        detail = _dac_get(f"/ai-signals?date={date}")
        signals = detail.get("signals", [])
    except Exception as exc:
        logger.warning("dac_ai_signals detail failed: %s", exc)
        signals = []

    count = latest_active.get("signal_count", len(signals))
    lines = [f"Tín hiệu AI breakout gần nhất của Đông Anh Capital: ngày {date}, {count} mã."]
    for sig in signals[:3]:
        lines.append(
            f"Mã {sig['stock_id']}: giá vào {sig['entry_price']:g} nghìn đồng, "
            f"mục tiêu {sig['tp_price']:g}, cắt lỗ {sig['sl_price']:g}."
        )
    lines.append(
        "Lưu ý: tín hiệu chỉ mang tính tham khảo, không phải lời khuyên đầu tư. "
        "Muốn phân tích sâu hơn, hãy hỏi Hiro trên Đông Anh Capital chấm com."
    )
    result = _voice_output(" ".join(lines))
    _dac_cache_put("dac_ai_signals_today", result)
    return result


@mcp.tool()
def dac_market_movers() -> str:
    """Lấy top cổ phiếu tăng/giảm mạnh nhất phiên từ Đông Anh Capital. Dùng khi người dùng hỏi mã nào tăng mạnh, giảm mạnh hoặc thị trường có gì nổi bật. Kết quả đã là câu hoàn chỉnh cho TTS; giữ nguyên khi đọc."""
    try:
        rows = _dac_get("/market-status")
    except Exception as exc:
        logger.warning("dac_market_movers failed: %s", exc)
        return _dac_fallback("dac_market_movers")

    # Chỉ xét mã có thanh khoản đáng kể để tránh mã tăng trần với vài trăm cổ phiếu khớp lệnh
    liquid = [r for r in rows if (r.get("trading_value") or 0) >= 1_000_000 and r.get("value") is not None]
    if not liquid:
        return _voice_output("Chưa có dữ liệu thị trường hôm nay.")

    gainers = sorted(liquid, key=lambda r: r["value"], reverse=True)[:3]
    losers = sorted(liquid, key=lambda r: r["value"])[:3]

    def fmt(items):
        return ", ".join(f"{r['ticker']} ({r['value']:+.1f}%)" for r in items)

    result = (
        f"Top tăng: {fmt(gainers)}. Top giảm: {fmt(losers)}. "
        "Dữ liệu từ Đông Anh Capital chấm com, chỉ mang tính tham khảo."
    )
    result = _voice_output(result)
    _dac_cache_put("dac_market_movers", result)
    return result


if __name__ == "__main__":
    mcp.run(transport="stdio")
