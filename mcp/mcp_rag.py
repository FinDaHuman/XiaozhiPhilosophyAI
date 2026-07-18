import json
import logging
import os
import sys
import urllib.request
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from rag_pipeline_faiss import INDEX_FILE, ask, ingest, iter_documents, load_index, retrieve


if sys.platform == "win32":
    sys.stderr.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")


load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RAG_MCP")

mcp = FastMCP("LocalRAG")

DAC_API = os.getenv("DAC_API", "https://donganhcapital.onrender.com/api")
DAC_TIMEOUT = 12  # giay; Render free co the ngu (cold start ~60s) — khong doi lau de robot khong bi treo
DAC_OFFLINE_MSG = (
    "May chu DongAnh Capital dang khoi dong lai, chua co du lieu ngay. "
    "Ban co the xem truc tiep tai donganhcapital.com hoac hoi lai sau mot phut."
)
DAC_STALE_PREFIX = "May chu DongAnh Capital dang khoi dong lai. So lieu phien gan nhat minh co: "
DAC_CACHE_FILE = Path(__file__).resolve().parent / ".dac_cache.json"

# Cache ket qua da format cua cac tool dac_* (chuoi chua san ngay phien nen tu mo ta duoc).
# Giu ca ban tren dia de song sot qua restart process.
_dac_cache: dict = {}


def _dac_cache_load() -> None:
    global _dac_cache
    try:
        _dac_cache = json.loads(DAC_CACHE_FILE.read_text(encoding="utf-8"))
    except Exception:
        _dac_cache = {}


def _dac_cache_put(tool: str, text: str) -> None:
    _dac_cache[tool] = text
    try:
        DAC_CACHE_FILE.write_text(json.dumps(_dac_cache, ensure_ascii=False), encoding="utf-8")
    except OSError as exc:
        logger.warning("Khong ghi duoc DAC cache: %s", exc)


def _dac_cache_get(tool: str):
    return _dac_cache.get(tool)


_dac_cache_load()


def _dac_get(path: str):
    """GET mot endpoint public cua donganhcapital.com, tra ve JSON da parse."""
    url = f"{DAC_API}{path}"
    request = urllib.request.Request(url, headers={"User-Agent": "LilyRobot/1.0"})
    with urllib.request.urlopen(request, timeout=DAC_TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def _dac_fallback(tool: str) -> str:
    """Cau tra loi khi API DAC khong phan hoi: uu tien so lieu cache gan nhat."""
    cached = _dac_cache_get(tool)
    if cached:
        return DAC_STALE_PREFIX + cached
    return DAC_OFFLINE_MSG


# Backend web Lily (cung may): bo nao RAG manh hon (ChromaDB + e5 + Groq 70B)
# voi persona giong noi rieng. Neu backend tat thi rag_answer tu fallback FAISS.
WEB_BACKEND = os.getenv("LILY_WEB_BACKEND", "http://127.0.0.1:8000")
WEB_PROBE_TIMEOUT = 2    # giay — chi de biet backend co bat khong
WEB_ANSWER_TIMEOUT = 45  # giay — retrieval + LLM can thoi gian that


def _ask_web_backend(question: str):
    """Tra ve cau tra loi tu backend web local, hoac None de caller fallback FAISS."""
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
    """Tim cac doan lien quan trong kho tai lieu local."""
    try:
        contexts = retrieve(question, top_k=top_k)
    except Exception as exc:
        logger.exception("RAG search failed")
        return f"Loi khi tim kiem RAG: {exc}"

    logger.info("RAG search: %s | results=%s", question, len(contexts))
    if not contexts:
        return "Khong tim thay doan nao lien quan trong kho tai lieu local."

    lines = ["Ket qua tim kiem RAG:"]
    for idx, (chunk, score) in enumerate(contexts, start=1):
        lines.append(
            f"\n{idx}. Nguon: {chunk.source}\n"
            f"Do lien quan: {score:.3f}\n"
            f"Noi dung: {chunk.text}"
        )
    return "\n".join(lines)


@mcp.tool()
def rag_answer(question: str, top_k: int = 4) -> str:
    """Tra loi cau hoi dua tren kho tai lieu local va Groq."""
    answer = _ask_web_backend(question)
    if answer:
        logger.info("RAG answer (web backend): %s", question)
        return answer

    try:
        answer = ask(question, top_k=top_k)
    except Exception as exc:
        logger.exception("RAG answer failed")
        return f"Loi khi tra loi RAG: {exc}"

    logger.info("RAG answer (FAISS): %s", question)
    return answer


@mcp.tool()
def rag_reindex() -> str:
    """Tao lai FAISS index tu cac file trong thu muc data."""
    try:
        ingest()
    except Exception as exc:
        logger.exception("RAG reindex failed")
        return f"Loi khi tao lai index RAG: {exc}"

    logger.info("RAG index rebuilt")
    return "Da tao lai FAISS index tu thu muc data/."


@mcp.tool()
def rag_status() -> str:
    """Kiem tra tai lieu va FAISS index hien co cua RAG local."""
    documents = iter_documents()
    lines = [
        "Trang thai RAG local:",
        f"- So file tai lieu trong data/: {len(documents)}",
        f"- FAISS index ton tai: {'co' if INDEX_FILE.exists() else 'khong'}",
    ]

    for path in documents[:20]:
        lines.append(f"- Tai lieu: {path.name}")

    if INDEX_FILE.exists():
        try:
            index = load_index()
            lines.append(f"- So chunk trong index: {len(index.get('chunks', []))}")
        except Exception as exc:
            lines.append(f"- Khong doc duoc index: {exc}")

    return "\n".join(lines)


@mcp.tool()
def dac_vnindex() -> str:
    """Lay chi so VNINDEX moi nhat (diem so, thay doi phien gan nhat) tu nen tang chung khoan DongAnh Capital (donganhcapital.com). Dung khi nguoi dung hoi VNINDEX hom nay the nao, thi truong chung khoan Viet Nam ra sao."""
    try:
        rows = _dac_get("/vnindex?limit=2")
    except Exception as exc:
        logger.warning("dac_vnindex failed: %s", exc)
        return _dac_fallback("dac_vnindex")

    if not rows:
        return "Chua co du lieu VNINDEX."

    latest = rows[-1]
    close = latest["Close"]
    date = str(latest["Date"])[:10]
    line = f"VNINDEX phien {date}: dong cua {close:,.2f} diem"
    if len(rows) >= 2:
        prev_close = rows[-2]["Close"]
        change = close - prev_close
        pct = change / prev_close * 100 if prev_close else 0
        direction = "tang" if change >= 0 else "giam"
        line += f", {direction} {abs(change):,.2f} diem ({pct:+.2f}%) so voi phien truoc"
    volume = latest.get("Volume")
    if volume:
        line += f". Khoi luong {volume / 1_000_000:,.0f} trieu don vi."
    _dac_cache_put("dac_vnindex", line)
    return line


@mcp.tool()
def dac_ai_signals_today() -> str:
    """Lay tin hieu AI breakout (dot pha gia) moi nhat tu nen tang chung khoan DongAnh Capital (donganhcapital.com). Dung khi nguoi dung hoi hom nay co tin hieu AI / goi y co phieu nao khong."""
    try:
        summary = _dac_get("/ai-signals/summary")
    except Exception as exc:
        logger.warning("dac_ai_signals_today failed: %s", exc)
        return _dac_fallback("dac_ai_signals_today")

    latest_active = next((row for row in summary if row.get("signal_count", 0) > 0), None)
    if latest_active is None:
        return "Gan day mo hinh AI cua DongAnh Capital chua phat tin hieu breakout nao — mo hinh rat chon loc, chi bao khi xac suat du tot."

    date = latest_active["date"]
    try:
        detail = _dac_get(f"/ai-signals?date={date}")
        signals = detail.get("signals", [])
    except Exception as exc:
        logger.warning("dac_ai_signals detail failed: %s", exc)
        signals = []

    count = latest_active.get("signal_count", len(signals))
    lines = [f"Tin hieu AI breakout gan nhat cua DongAnh Capital: ngay {date}, {count} ma."]
    for sig in signals[:3]:
        lines.append(
            f"Ma {sig['stock_id']}: gia vao {sig['entry_price']:g} nghin dong, "
            f"muc tieu {sig['tp_price']:g}, cat lo {sig['sl_price']:g}."
        )
    lines.append("Luu y: tin hieu chi mang tinh tham khao, khong phai loi khuyen dau tu. Muon phan tich sau hon, hay hoi Hiro tren donganhcapital.com.")
    result = " ".join(lines)
    _dac_cache_put("dac_ai_signals_today", result)
    return result


@mcp.tool()
def dac_market_movers() -> str:
    """Lay top co phieu tang/giam manh nhat phien tu nen tang chung khoan DongAnh Capital (donganhcapital.com). Dung khi nguoi dung hoi co phieu nao tang manh, giam manh, thi truong co gi noi bat."""
    try:
        rows = _dac_get("/market-status")
    except Exception as exc:
        logger.warning("dac_market_movers failed: %s", exc)
        return _dac_fallback("dac_market_movers")

    # Chi xet ma co thanh khoan dang ke de tranh ma tang tran voi vai tram co phieu khop lenh
    liquid = [r for r in rows if (r.get("trading_value") or 0) >= 1_000_000 and r.get("value") is not None]
    if not liquid:
        return "Chua co du lieu thi truong hom nay."

    gainers = sorted(liquid, key=lambda r: r["value"], reverse=True)[:3]
    losers = sorted(liquid, key=lambda r: r["value"])[:3]

    def fmt(items):
        return ", ".join(f"{r['ticker']} ({r['value']:+.1f}%)" for r in items)

    result = (
        f"Top tang: {fmt(gainers)}. Top giam: {fmt(losers)}. "
        "Du lieu tu donganhcapital.com, chi mang tinh tham khao."
    )
    _dac_cache_put("dac_market_movers", result)
    return result


if __name__ == "__main__":
    mcp.run(transport="stdio")
