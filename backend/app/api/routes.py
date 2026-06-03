"""
FastAPI Routes

Provides REST API endpoints for the philosophy RAG:
  POST /chat     — Ask a philosophy question
  GET  /health   — Health check
  POST /reload   — Reload knowledge base
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.rag.pipeline import RAGPipeline

router = APIRouter()

# Shared RAG pipeline instance
rag = RAGPipeline()


# ─── Request/Response Models ────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str


class HealthResponse(BaseModel):
    status: str


class ReloadResponse(BaseModel):
    status: str
    stats: dict


# ─── Endpoints ──────────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Ask a philosophy question.
    The RAG pipeline retrieves relevant documents and generates an answer.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        answer = rag.ask(request.message)
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")


@router.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(status="ok")


@router.post("/reload", response_model=ReloadResponse)
async def reload():
    """
    Reload the knowledge base.
    Re-ingests all documents from the data/ directory.
    """
    try:
        result = rag.reload_knowledge_base()
        return ReloadResponse(status=result["status"], stats=result["stats"])
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reloading knowledge base: {str(e)}"
        )


@router.get("/stats")
async def stats():
    """Get pipeline statistics."""
    return rag.get_stats()
