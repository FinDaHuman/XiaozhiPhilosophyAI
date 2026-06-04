import logging
import sys

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
    try:
        answer = ask(question, top_k=top_k)
    except Exception as exc:
        logger.exception("RAG answer failed")
        return f"Loi khi tra loi RAG: {exc}"

    logger.info("RAG answer: %s", question)
    return answer


@mcp.tool()
def rag_reindex() -> str:
    """Tao lai FAISS index tu cac file trong thu muc docs."""
    try:
        ingest()
    except Exception as exc:
        logger.exception("RAG reindex failed")
        return f"Loi khi tao lai index RAG: {exc}"

    logger.info("RAG index rebuilt")
    return "Da tao lai FAISS index tu thu muc docs/."


@mcp.tool()
def rag_status() -> str:
    """Kiem tra tai lieu va FAISS index hien co cua RAG local."""
    documents = iter_documents()
    lines = [
        "Trang thai RAG local:",
        f"- So file tai lieu trong docs/: {len(documents)}",
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


if __name__ == "__main__":
    mcp.run(transport="stdio")
