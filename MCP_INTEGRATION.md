# MCP Integration Guide

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Xiaozhi Robot (小智)                                        │
│  ┌────────────────────────┐                                  │
│  │  mcp/                  │  ← MCP Integration               │
│  │  ├── mcp_rag.py        │     MCP tool server (stdio)      │
│  │  ├── mcp_pipe.py       │     WebSocket ↔ stdio bridge     │
│  │  └── rag_pipeline_faiss.py Lightweight FAISS + TF-IDF pipeline │
│  └────────────────────────┘                                  │
│                                                              │
│  ┌────────────────────────┐                                  │
│  │  app/                  │  ← Main backend (FastAPI + CLI)  │
│  │  ├── rag/              │     ChromaDB + HuggingFace + Groq│
│  │  ├── api/              │     REST API (POST /chat)        │
│  │  └── ui/               │     Terminal chat UI             │
│  └────────────────────────┘                                  │
│                                                              │
│  ┌────────────────────────┐                                  │
│  │  data/                 │  ← Source documents              │
│  └────────────────────────┘                                  │
└─────────────────────────────────────────────────────────────┘
```

Both pipelines use **Groq API** for LLM generation.
Both pipelines use **local embeddings** (no external embedding API needed).

---

## Environment Variables

### Shared `.env`

| Variable           | Description                  | Example                          |
| ------------------ | ---------------------------- | -------------------------------- |
| `GROQ_API_KEY`     | Groq API key                 | `gsk_...`                        |
| `GROQ_MODEL`       | Groq model name              | `llama-3.1-8b-instant`           |
| `MCP_ENDPOINT`     | Xiaozhi MCP WebSocket endpoint | `wss://api.xiaozhi.me/mcp/...` |
| `EMBEDDING_MODEL`  | HuggingFace embedding model  | `intfloat/multilingual-e5-small` |
| `CHROMA_PERSIST_DIR` | ChromaDB storage path      | `chroma_db`                      |
| `CHROMA_COLLECTION`  | ChromaDB collection name   | `philosophy_docs`                |
| `TOP_K`            | Number of chunks to retrieve | `6`                              |

---

## Startup Commands

### 1. Backend — Terminal Chat

```bash
python main.py terminal
```

### 2. Backend — FastAPI Server

```bash
python main.py api
# Docs at http://localhost:8000/docs
```

### 3. Backend — Ingest Documents

```bash
python main.py ingest
```

### 4. MCP — Ingest Documents

```bash
cd mcp
python rag_pipeline_faiss.py ingest
```

### 5. MCP — Connect to Xiaozhi Robot

```bash
cd mcp
python mcp_pipe.py
```

This starts the WebSocket bridge that connects `mcp_rag.py` (stdio MCP server) to the Xiaozhi cloud endpoint.

---

## MCP Tools

The MCP server (`mcp_rag.py`) exposes 4 tools:

| Tool           | Description                                      | Parameters                          |
| -------------- | ------------------------------------------------ | ----------------------------------- |
| `rag_search`   | Search for relevant chunks in local docs         | `question: str`, `top_k: int = 4`  |
| `rag_answer`   | Answer a question using RAG + Groq               | `question: str`, `top_k: int = 4`  |
| `rag_reindex`  | Rebuild FAISS index from `data/` folder          | _(none)_                            |
| `rag_status`   | Check document count and index status            | _(none)_                            |

### Example Tool Call (JSON-RPC over stdio)

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "rag_answer",
    "arguments": {
      "question": "Mâu thuẫn biện chứng là gì?"
    }
  }
}
```

### Expected Response

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Mâu thuẫn biện chứng là sự thống nhất và đấu tranh giữa các mặt đối lập..."
      }
    ]
  }
}
```

---

## Two RAG Pipelines

| Feature          | `app/rag/` (ChromaDB)                | `mcp/` (FAISS)                     |
| ---------------- | ------------------------------------ | ---------------------------------- |
| Vector store     | ChromaDB (persistent)                | FAISS (pickle file)                |
| Embeddings       | HuggingFace E5 (multilingual)        | TF-IDF (scikit-learn)              |
| LLM              | Groq                                 | Groq                               |
| Interface        | FastAPI + Terminal UI                | MCP tools (stdio)                  |
| Documents        | `data/` folder                       | `data/` folder                     |
| Use case         | Development & API                    | Robot MCP integration              |

---

## Troubleshooting

**"RESOURCE_EXHAUSTED" / 429 error**
→ This was the old Gemini API issue. Now using Groq which has much higher rate limits on the free tier (30 req/min for llama-3.1-8b-instant).

**"Missing GROQ_API_KEY"**
→ Check that `.env` file exists in the correct directory and contains `GROQ_API_KEY=gsk_...`

**"Chua co index" error**
→ Run `python rag_pipeline_faiss.py ingest` (MCP) or `python main.py ingest` (ChromaDB) first.

**MCP pipe disconnects**
→ Check that `MCP_ENDPOINT` JWT token hasn't expired. The pipe auto-reconnects with exponential backoff.
