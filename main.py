"""
Lily Philosophy AI — Main Entry Point

Usage:
    python main.py terminal     Launch the terminal chat UI
    python main.py api          Start the FastAPI server
    python main.py ingest       Run the document ingestion pipeline
"""

import sys
import os

# Fix Windows console encoding for emoji/Unicode output
if os.name == "nt":
    os.system("chcp 65001 >nul 2>&1")
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
if sys.stdin and hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")

# Ensure the root directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

load_dotenv()


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "terminal":
        run_terminal()
    elif command == "api":
        run_api()
    elif command == "web":
        run_web()
    elif command == "ingest":
        run_ingest()
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()
        sys.exit(1)


def run_terminal():
    """Launch the Textual terminal UI."""
    print("🚀 Starting Lily Philosophy AI Terminal...")
    from app.ui.terminal import run_terminal as start_tui
    start_tui()


def run_api():
    """Start the FastAPI server."""
    import uvicorn
    from fastapi import FastAPI
    from app.api.routes import router

    from fastapi.middleware.cors import CORSMiddleware

    app = FastAPI(
        title="Lily Philosophy AI",
        description="API cho trợ lý AI Triết học Mác-Lênin",
        version="1.0.0",
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(router)

    print("🚀 Starting Lily Philosophy AI API...")
    print("📖 Docs: http://localhost:8000/docs")

    uvicorn.run(app, host="0.0.0.0", port=8000)


def run_web():
    """Start the FastAPI server for the learning website."""
    import uvicorn
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    from app.api.routes import router

    from fastapi.middleware.cors import CORSMiddleware

    # Pre-extract slides
    print("📚 Extracting lesson slides from PDF...")
    try:
        from app.api.slide_extractor import extract_all_lesson_slides
        result = extract_all_lesson_slides()
        total = sum(len(v) for v in result.values())
        print(f"✅ Extracted {total} slide images")
    except Exception as e:
        print(f"⚠️ Slide extraction warning: {e}")
        print("   Slides will be extracted on-demand when accessed.")

    app = FastAPI(
        title="Triết học Mác-Lênin — Quy luật Mâu thuẫn",
        description="Website học Triết học Mác-Lênin với AI",
        version="1.0.0",
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(router)

    print("")
    print("🌐 ═══════════════════════════════════════════")
    print("   Triết học Mác-Lênin — Learning Website")
    print("   http://localhost:8000")
    print("═══════════════════════════════════════════════")
    print("")

    uvicorn.run(app, host="0.0.0.0", port=8000)


def run_ingest():
    """Run the document ingestion pipeline."""
    from app.rag.ingest import run_ingest_pipeline
    resume = "--resume" in sys.argv
    run_ingest_pipeline(resume=resume)


def print_usage():
    print("""
╔══════════════════════════════════════════════╗
║       Lily Philosophy AI        ║
╠══════════════════════════════════════════════╣
║                                              ║
║  Usage:                                      ║
║    python main.py <command>                  ║
║                                              ║
║  Commands:                                   ║
║    web       Start learning website          ║
║    ingest    Ingest documents into KB         ║
║    terminal  Launch terminal chat UI          ║
║    api       Start FastAPI server             ║
║                                              ║
╚══════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()
