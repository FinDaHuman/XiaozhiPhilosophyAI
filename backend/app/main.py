"""
Xiaozhi Philosophy AI — Main Entry Point

Usage:
    python -m app.main terminal     Launch the terminal chat UI
    python -m app.main api          Start the FastAPI server
    python -m app.main ingest       Run the document ingestion pipeline
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

# Ensure the backend directory is in the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    elif command == "ingest":
        run_ingest()
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()
        sys.exit(1)


def run_terminal():
    """Launch the Textual terminal UI."""
    print("🚀 Starting Xiaozhi Philosophy AI Terminal...")
    from app.ui.terminal import run_terminal as start_tui
    start_tui()


def run_api():
    """Start the FastAPI server."""
    import uvicorn
    from fastapi import FastAPI
    from app.api.routes import router

    app = FastAPI(
        title="Xiaozhi Philosophy AI",
        description="API cho trợ lý AI Triết học Mác-Lênin",
        version="1.0.0",
    )
    app.include_router(router)

    print("🚀 Starting Xiaozhi Philosophy AI API...")
    print("📖 Docs: http://localhost:8000/docs")

    uvicorn.run(app, host="0.0.0.0", port=8000)


def run_ingest():
    """Run the document ingestion pipeline."""
    from app.rag.ingest import run_ingest_pipeline
    resume = "--resume" in sys.argv
    run_ingest_pipeline(resume=resume)


def print_usage():
    print("""
╔══════════════════════════════════════════════╗
║       Xiaozhi Philosophy AI (小智哲学)        ║
╠══════════════════════════════════════════════╣
║                                              ║
║  Usage:                                      ║
║    python -m app.main <command>               ║
║                                              ║
║  Commands:                                   ║
║    ingest    Ingest documents into KB         ║
║    terminal  Launch terminal chat UI          ║
║    api       Start FastAPI server             ║
║                                              ║
╚══════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()
