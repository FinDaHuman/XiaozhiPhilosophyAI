"""
FastAPI Routes

Provides REST API endpoints for the philosophy RAG:
  POST /chat     — Ask a philosophy question
  GET  /health   — Health check
  POST /reload   — Reload knowledge base
  GET  /api/lessons — Get lesson structure
  GET  /api/slides/{page} — Get slide image
  WS   /ws/mcp   — WebSocket bridge to MCP RAG server
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

from app.api.slide_extractor import extract_slide, get_lessons_json, parse_chia_slide

logger = logging.getLogger("WEB_ROUTES")

router = APIRouter()

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
WEBCONTENT_DIR = BASE_DIR / "webcontent"
MCP_DIR = BASE_DIR / "mcp"


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


# ─── Static File Serving ────────────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the main index.html page."""
    index_path = WEBCONTENT_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(str(index_path), media_type="text/html")


@router.get("/styles.css")
async def serve_css():
    """Serve the main CSS file."""
    css_path = WEBCONTENT_DIR / "styles.css"
    if not css_path.exists():
        raise HTTPException(status_code=404, detail="styles.css not found")
    return FileResponse(str(css_path), media_type="text/css")


@router.get("/app.js")
async def serve_js():
    """Serve the main JS file."""
    js_path = WEBCONTENT_DIR / "app.js"
    if not js_path.exists():
        raise HTTPException(status_code=404, detail="app.js not found")
    return FileResponse(str(js_path), media_type="application/javascript")


@router.get("/images/{filename}")
async def serve_image(filename: str):
    """Serve static images."""
    img_path = WEBCONTENT_DIR / "images" / filename
    if not img_path.exists():
        raise HTTPException(status_code=404, detail=f"Image {filename} not found")
    media_type = "image/png" if filename.endswith(".png") else "image/jpeg"
    return FileResponse(str(img_path), media_type=media_type)


# ─── Lesson & Slide API ────────────────────────────────────────────────────

@router.get("/api/lessons")
async def get_lessons():
    """Get lesson structure from ChiaSlide.txt."""
    return get_lessons_json()


@router.get("/api/slides/{page}")
async def get_slide(page: int):
    """Get a slide image by page number (1-indexed)."""
    slide_path = extract_slide(page)
    if slide_path is None or not slide_path.exists():
        raise HTTPException(status_code=404, detail=f"Slide {page} not found")
    return FileResponse(str(slide_path), media_type="image/png")


# ─── Quiz API ──────────────────────────────────────────────────────────────

@router.get("/api/quiz")
async def get_quiz():
    """Parse and return quiz questions from MLN111_Cau_hoi.txt."""
    quiz_path = WEBCONTENT_DIR / "MLN111_Cau_hoi.txt"
    if not quiz_path.exists():
        raise HTTPException(status_code=404, detail="Quiz file not found")

    questions = []
    answers = {}

    with open(quiz_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into questions section and answers section
    parts = content.split("Đáp án")
    if len(parts) < 2:
        raise HTTPException(status_code=500, detail="Cannot parse quiz file")

    question_text = parts[0]
    answer_text = parts[1]

    # Parse answers: "1. C", "2. B", etc.
    import re
    for line in answer_text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r'^(\d+)\.\s*([A-D])', line)
        if m:
            answers[int(m.group(1))] = m.group(2).strip()

    # Parse questions with regex scan — robust against header lines
    # Finds every "Câu N: ..." block including the first one
    pattern = re.compile(
        r'Câu\s+(\d+)\s*:\s*(.+?)(?=\r?\nCâu\s+\d+\s*:|\Z)',
        re.DOTALL
    )

    for m in pattern.finditer(question_text):
        q_num = int(m.group(1))
        block = m.group(2).strip()
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue

        q_text_lines = []
        options = []
        for ln in lines:
            opt_m = re.match(r'^([A-D])\.\s*(.*)', ln)
            if opt_m:
                options.append({"label": opt_m.group(1), "text": opt_m.group(2).strip()})
            elif not options:
                q_text_lines.append(ln)

        q_text = " ".join(q_text_lines).strip()
        if not q_text or not options:
            continue

        questions.append({
            "number": q_num,
            "question": q_text,
            "options": options,
            "correct": answers.get(q_num, ""),
        })

    questions.sort(key=lambda x: x["number"])
    return questions


# ─── MCP WebSocket Bridge ──────────────────────────────────────────────────

@router.websocket("/ws/mcp")
async def mcp_websocket(websocket: WebSocket):
    """
    WebSocket bridge: Browser ↔ MCP RAG server (stdio).

    Spawns mcp_rag.py as a subprocess and forwards JSON-RPC messages
    between the browser WebSocket and the MCP server's stdio.
    """
    await websocket.accept()
    logger.info("MCP WebSocket client connected")

    mcp_script = MCP_DIR / "mcp_rag.py"
    if not mcp_script.exists():
        await websocket.send_json({"error": "MCP RAG server not found"})
        await websocket.close()
        return

    process = None
    try:
        # Start the MCP RAG server process
        env = os.environ.copy()
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(mcp_script),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(MCP_DIR),
            env=env,
        )
        logger.info("MCP RAG process started (PID: %s)", process.pid)

        # Send initialization
        init_msg = json.dumps({
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "web-client", "version": "1.0.0"},
            },
        })
        process.stdin.write((init_msg + "\n").encode("utf-8"))
        await process.stdin.drain()

        # Read init response
        init_response = await asyncio.wait_for(
            process.stdout.readline(), timeout=30
        )
        if init_response:
            logger.info("MCP init response received")
            # Send initialized notification
            notif = json.dumps({
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
            })
            process.stdin.write((notif + "\n").encode("utf-8"))
            await process.stdin.drain()

        async def read_from_mcp():
            """Read responses from MCP process and send to WebSocket."""
            try:
                while True:
                    data = await process.stdout.readline()
                    if not data:
                        break
                    line = data.decode("utf-8").strip()
                    if line:
                        await websocket.send_text(line)
            except Exception as e:
                logger.debug("MCP read loop ended: %s", e)

        # Start background task to read MCP responses
        read_task = asyncio.create_task(read_from_mcp())

        # Main loop: read from WebSocket and write to MCP process
        try:
            while True:
                message = await websocket.receive_text()
                if process.stdin:
                    process.stdin.write((message + "\n").encode("utf-8"))
                    await process.stdin.drain()
        except WebSocketDisconnect:
            logger.info("MCP WebSocket client disconnected")
        finally:
            read_task.cancel()

    except Exception as e:
        logger.exception("MCP WebSocket error: %s", e)
        try:
            await websocket.send_json({"error": str(e)})
        except Exception:
            pass
    finally:
        if process:
            try:
                process.terminate()
            except Exception:
                pass
            try:
                await asyncio.wait_for(process.wait(), timeout=5)
            except Exception:
                try:
                    process.kill()
                except Exception:
                    pass
            logger.info("MCP RAG process terminated")


# ─── MCP Pipe Execution ──────────────────────────────────────────────────────

_mcp_pipe_process = None

@router.post("/api/start-mcp")
async def start_mcp_pipe():
    """Start the MCP Pipe background process if not already running."""
    global _mcp_pipe_process
    
    # Check if already running
    if _mcp_pipe_process is not None:
        if _mcp_pipe_process.poll() is None:
            return {"status": "already_running"}
            
    mcp_pipe_script = MCP_DIR / "mcp_pipe.py"
    if not mcp_pipe_script.exists():
        raise HTTPException(status_code=500, detail="mcp_pipe.py not found")
        
    try:
        env = os.environ.copy()
        # Ensure we run using the venv python
        _mcp_pipe_process = subprocess.Popen(
            [sys.executable, str(mcp_pipe_script)],
            cwd=str(MCP_DIR),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        )
        logger.info(f"Started mcp_pipe.py with PID {_mcp_pipe_process.pid}")
        return {"status": "started", "pid": _mcp_pipe_process.pid}
    except Exception as e:
        logger.error(f"Failed to start mcp_pipe: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Existing Endpoints ─────────────────────────────────────────────────────

# Lazy-load RAG pipeline only when needed
_rag = None


def get_rag():
    global _rag
    if _rag is None:
        from app.rag.pipeline import RAGPipeline
        _rag = RAGPipeline()
    return _rag


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Ask a philosophy question.
    The RAG pipeline retrieves relevant documents and generates an answer.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        answer = get_rag().ask(request.message)
        return ChatResponse(answer=answer)
    except Exception as e:
        import traceback
        traceback.print_exc()
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
        result = get_rag().reload_knowledge_base()
        return ReloadResponse(status=result["status"], stats=result["stats"])
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reloading knowledge base: {str(e)}"
        )


@router.get("/stats")
async def stats():
    """Get pipeline statistics."""
    return get_rag().get_stats()
