# Connect XiaoZhi Hardware to Lily

This guide connects XiaoZhi-compatible hardware to the Lily MCP server. The
device talks to the XiaoZhi cloud; `mcp/mcp_pipe.py` bridges that WebSocket to
the local stdio MCP server.

## Prerequisites

- A paired XiaoZhi device on a working network.
- A XiaoZhi account with access to the device's Agent/MCP settings.
- This repository installed with Python 3.11, a root `venv/`, and dependencies
  from both `requirements.txt` and `mcp/requirements.txt`.
- A root `.env` containing provider keys and the device-specific MCP endpoint.

## 1. Obtain the MCP endpoint

In the XiaoZhi console, open the device's Agent or Character settings, find the
MCP section, and copy the complete `wss://api.xiaozhi.me/mcp/...` endpoint. It
contains a credential: do not commit it, paste it into chat, or put it in logs.

## 2. Configure `.env`

Add the endpoint to the gitignored root `.env`:

```ini
MCP_ENDPOINT=wss://api.xiaozhi.me/mcp/your-private-token
GROQ_API_KEY=your-groq-key
GROQ_MODEL=llama-3.3-70b-versatile
GEMINI_API_KEY=your-gemini-key
GEMINI_MODEL=gemini-2.5-flash-lite
```

Groq is primary. Gemini is the fallback for supported transient Groq failures.
The same provider chain is shared by the web and FAISS generation paths.

## 3. Build both RAG stores

Both pipelines read supported PDF, DOCX, Markdown and text files from root
`data/`.

```powershell
# From repository root: web/API Chroma store
venv\Scripts\python main.py ingest

# Robot's local fallback store
cd mcp
..\venv\Scripts\python rag_pipeline_faiss.py ingest
cd ..
```

Rebuild both stores whenever source documents change. FAISS ingest overwrites
its generated index. Follow `GUIDE_KHOI_DONG.md` before rebuilding Chroma while
the backend is running.

## 4. Start Lily and the bridge

Preferred Windows operation:

```powershell
.\start_all.ps1
```

Manual operation uses two terminals:

```powershell
# Terminal 1: preferred Chroma-backed answer path
venv\Scripts\python main.py api
```

```powershell
# Terminal 2: XiaoZhi WebSocket-to-MCP bridge
cd mcp
..\venv\Scripts\python mcp_pipe.py
```

Keep the bridge terminal running. A successful connection makes seven tools
available: four local RAG tools plus three DongAnh Capital live-data tools.

## How robot answers are produced

For `rag_answer`, the MCP server probes local `/health` and calls `/chat/robot`.
That route uses the stronger Chroma/E5 hybrid retriever and returns a short
spoken answer. If the backend is down or times out, the tool falls back to the
local FAISS/TF-IDF index. The robot therefore remains usable without the web
backend as long as the FAISS index and an LLM provider are available.

`rag_search` always searches FAISS directly. The DAC tools query public
DongAnh Capital endpoints and may return the latest disk-cached response during
an outage. Their output is informational, not investment advice.

## Validation checklist

1. `GET http://localhost:8000/health` returns `{"status":"ok"}`.
2. `mcp_pipe.py` reports a successful WebSocket connection.
3. Ask one MLN111 question and one KTCT question through the device.
4. Ask for the latest VNINDEX data to exercise a DAC tool.
5. Stop only the FastAPI backend and ask another course question; a FAISS-backed
   answer confirms the fallback path.
6. Listen for voice formatting: answers should be short, without markdown or
   bracketed citations.

## Troubleshooting

- **Endpoint rejected or frequent disconnects:** refresh `MCP_ENDPOINT` in
  `.env`; never share the token. The pipe reconnects with backoff.
- **No index / no context:** run `mcp/rag_pipeline_faiss.py ingest` and verify
  source files exist in `data/`.
- **Bridge launches the wrong Python:** `mcp/mcp_config.json` should point to
  `../venv/Scripts/python.exe` on Windows.
- **Backend answers fail but FAISS works:** check port 8000 and the backend logs.
- **Provider quota failure:** configure both Groq and Gemini or wait for quota
  reset. See `MCP_INTEGRATION.md` for retry behavior.
