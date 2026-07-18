# MCP Integration Guide

## Architecture

```text
XiaoZhi hardware
  -> XiaoZhi cloud WebSocket
  -> mcp/mcp_pipe.py
  -> mcp/mcp_rag.py (stdio MCP server, 7 tools)
       -> local FastAPI /chat/robot (preferred answer path)
       -> mcp/rag_pipeline_faiss.py (FAISS + TF-IDF fallback)
       -> DongAnh Capital public APIs (3 live-data tools)

Web / terminal
  -> app/rag/ (ChromaDB + E5 + BM25 + MultiQuery)

Both RAG stores ingest the root data/ directory.
Both generation paths use Groq first and Gemini as a transient-error fallback.
```

## Spoken-output contract

Every hardware-facing answer passes through `app/rag/voice.py` before it leaves
the local MCP server. The contract is deterministic:

- `DongAnh Capital`, `DongAnhCapital`, `DonganhCapital` and spacing/case
  variants become `Đông Anh Capital`;
- `donganhcapital.com`, including `http(s)` and `www` forms, becomes
  `Đông Anh Capital chấm com`;
- the transformation is idempotent and also applies to disk-cached DAC output;
- prompts and direct tool responses use Vietnamese diacritics so TTS does not
  have to infer Vietnamese words from ASCII text.

The XiaoZhi Agent prompt must repeat this pronunciation contract because the
cloud Agent sits after MCP and may paraphrase a tool result. See section 2 of
`XIAOZHI_HARDWARE_SETUP.md` for the exact prompt block and hardware acceptance
steps. SSML is intentionally not emitted because this integration sends plain
text and does not control which cloud TTS provider is selected.

Hiro is an external advisor on `donganhcapital.com`; this repository only
contains Lily's knowledge and referrals to Hiro.

## Environment

The bridge and both pipelines load the root `.env`. Keep it gitignored and do
not copy secret values into documentation or logs.

| Variable | Purpose | Default/example |
| --- | --- | --- |
| `GROQ_API_KEY` | Primary generation provider | required for normal primary path |
| `GROQ_MODEL` | Shared Groq model | `llama-3.3-70b-versatile` |
| `GEMINI_API_KEY` | Fallback generation provider | optional but recommended |
| `GEMINI_MODEL` | Gemini fallback model | `gemini-2.5-flash-lite` |
| `MCP_ENDPOINT` | XiaoZhi MCP WebSocket URL | `wss://api.xiaozhi.me/mcp/...` |
| `LILY_WEB_BACKEND` | Preferred robot answer backend | `http://127.0.0.1:8000` |
| `DAC_API` | DongAnh Capital API override | production public API |
| `EMBEDDING_MODEL` | Web embedding model | `intfloat/multilingual-e5-small` |
| `CHROMA_PERSIST_DIR` | Web vector store | `chroma_db` |
| `CHROMA_COLLECTION` | Chroma collection | `philosophy_docs` |
| `TOP_K` | Web retriever result count | code default `5`; root `.env` may override |

MCP tools take their own `top_k` argument with a default of 4. That is separate
from the web retriever's `TOP_K` environment setting.

## Install and ingest

From the repository root with the virtual environment activated:

```powershell
pip install -r requirements.txt
pip install -r mcp/requirements.txt

# Chroma web/API store
python main.py ingest

# FAISS robot fallback store
cd mcp
..\venv\Scripts\python rag_pipeline_faiss.py ingest
```

The Chroma chunk configuration is 1000 characters with 200 overlap. The FAISS
fallback uses 900 characters with 150 overlap. Stored chunk counts are generated
artifacts and can change after any ingest, so query `/stats` and `rag_status`
instead of relying on documentation snapshots.

## Start services

The normal Windows path starts backend, ngrok, robot bridge, and DAC warm-up:

```powershell
.\start_all.ps1
```

For manual operation:

```powershell
venv\Scripts\python main.py api
cd mcp
..\venv\Scripts\python mcp_pipe.py
```

`mcp_pipe.py` launches `mcp_rag.py` over stdio and reconnects to the configured
XiaoZhi WebSocket with backoff. See `GUIDE_KHOI_DONG.md` for the full operations
procedure and `XIAOZHI_HARDWARE_SETUP.md` for device pairing.

## MCP tools

`mcp/mcp_rag.py` exposes seven tools:

| Tool | Behavior | Parameters |
| --- | --- | --- |
| `rag_search` | Search relevant FAISS/TF-IDF chunks | `question`, `top_k=4` |
| `rag_answer` | Try `/chat/robot`; fallback to local FAISS answer | `question`, `top_k=4` |
| `rag_reindex` | Rebuild FAISS from `data/` | none |
| `rag_status` | Report files and FAISS index state | none |
| `dac_vnindex` | Latest VNINDEX session and change | none |
| `dac_ai_signals_today` | Latest available DAC AI breakout signals | none |
| `dac_market_movers` | Most active gainers and losers | none |

The three DAC tools cache successful responses in `mcp/.dac_cache.json`. When
the upstream API is unavailable they return the latest cached value when one
exists. Market output is informational and must not be presented as a promise
of return or personalized investment advice.

Cache values are normalized both when loaded and when written. The cache format
is versioned; an old unversioned ASCII cache is rejected instead of being read
aloud without Vietnamese diacritics. Restart the MCP bridge after upgrading,
then prime all three DAC tools before the presentation.

## Knowledge-source priority

The upcoming presentation treats Đông Anh Capital as the active knowledge
domain. Ambiguous questions, including generic references to "the
presentation", are retrieved only from `DongAnhCapital_KnowledgeBase.md`.
MLN111, KTCT, slides, and legacy textbooks are selected only when the question
contains an explicit subject marker. This routing is shared by the preferred
ChromaDB backend and the local FAISS fallback.

## Robot answer fallback

`rag_answer` follows this order:

1. probe `GET {LILY_WEB_BACKEND}/health` with a short timeout;
2. call `POST {LILY_WEB_BACKEND}/chat/robot` for the Chroma-backed voice answer;
3. if either request fails, retrieve from the local FAISS index and generate a
   short voice-safe answer;
4. within either generation path, use Groq first and switch to Gemini only for
   supported transient failures before output begins.

`rag_search` always searches the local FAISS index directly.

## Troubleshooting

- **No FAISS index:** run `rag_pipeline_faiss.py ingest` from `mcp/`.
- **No Chroma store:** run `python main.py ingest` from the repository root.
- **MCP disconnects:** confirm `MCP_ENDPOINT` is present and current; never paste
  its token into an issue or log.
- **Groq 429/timeout/5xx:** generation switches to Gemini when configured.
  Gemini 429 responses are not retried; eligible Gemini 5xx failures retry once.
- **Backend unavailable:** robot RAG can still answer through FAISS, but the
  backend, streaming web chat, and Chroma retrieval remain unavailable.
