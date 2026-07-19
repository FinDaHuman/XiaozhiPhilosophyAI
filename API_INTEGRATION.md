# Lily API Integration

FastAPI serves the RAG chat API at `http://localhost:8000`. Interactive OpenAPI
documentation is available at `/docs` while the backend is running.

## Chat request model

`POST /chat`, `POST /chat/stream`, and `POST /chat/robot` accept:

```json
{
  "message": "Mâu thuẫn biện chứng là gì?",
  "history": [
    { "role": "user", "content": "Câu hỏi trước" },
    { "role": "assistant", "content": "Câu trả lời trước" }
  ]
}
```

`message` must contain non-whitespace text. `history` is optional:

- omitted: preserve the legacy shared backend conversation history;
- `[]`: start a fresh request with no prior turns;
- populated: use the supplied `user`/`assistant` turns as context.

## Chat endpoints

### `POST /chat`

Returns a normal web answer:

```json
{ "answer": "..." }
```

### `POST /chat/stream`

Returns `text/event-stream`. Each token is JSON-wrapped so embedded newlines do
not break SSE framing:

```text
data: {"token":"Mâu thuẫn"}

data: {"token":" biện chứng..."}

data: {"done":true}
```

If generation fails after the stream opens, the final event contains
`{"error":"..."}`. The bundled frontend falls back to `POST /chat` when the
stream request fails.

### `POST /chat/robot`

Returns the same `{ "answer": "..." }` envelope, but uses a short spoken
persona without markdown or citation brackets. It is stateless and ignores
`history`.

### `POST /chat/hiro`

Accepts the same `{ "message", "history" }` body and returns `{ "answer" }`.
The Lily backend forwards the bounded conversation to DongAnh Capital's
presentation-only Hiro endpoint. Configure `DAC_HIRO_INTERNAL_TOKEN` on Lily
and the matching `HIRO_INTERNAL_TOKEN` on DongAnh Capital. Optionally override
the upstream URL with `DAC_HIRO_API_URL`.

### Rate limiting

All three chat endpoints share a sliding-window limit of 20 requests per 60
seconds per client IP. Loopback clients (`127.0.0.1`, `::1`, `localhost`) are
exempt so the local robot bridge is not throttled. A rejected request returns
HTTP 429.

## Operations endpoints

### `GET /health`

```json
{ "status": "ok" }
```

### `GET /stats`

The values are runtime-dependent; do not hard-code document counts. The example
below matches the local store snapshot verified on 2026-07-18.

```json
{
  "model": "llama-3.3-70b-versatile",
  "conversation_turns": 0,
  "knowledge_base": {
    "collection_name": "philosophy_docs",
    "document_count": 1579,
    "persist_directory": "chroma_db",
    "embedding_model": "intfloat/multilingual-e5-small",
    "hybrid_search": true,
    "multi_query": true
  }
}
```

### `POST /reload`

Re-ingests the root `data/` directory and reloads the Chroma retriever. This can
be expensive; do not expose it to untrusted callers without authentication.

```json
{
  "status": "reloaded",
  "stats": {
    "collection_name": "philosophy_docs",
    "document_count": 1579,
    "persist_directory": "chroma_db",
    "embedding_model": "intfloat/multilingual-e5-small",
    "hybrid_search": true,
    "multi_query": true
  }
}
```

## Robot bridge endpoints

### `POST /api/start-mcp`

Starts `mcp/mcp_pipe.py` as a child process when it is not already running.
Possible success payloads are:

```json
{ "status": "started", "pid": 12345 }
```

```json
{ "status": "already_running" }
```

### `WS /ws/mcp`

WebSocket bridge used by the browser/robot integration. It is not a REST
endpoint; clients must speak the message protocol implemented in
`app/api/routes.py`.

## Legacy content endpoints

`GET /api/lessons`, `GET /api/slides/{page}`, and `GET /api/quiz` serve the
older `webcontent/` assets. The current React app primarily uses its bundled
two-subject data in `frontend/src/data/subjects.js`.

## Production access

The frontend resolves its backend in this order:

1. `localStorage.LILY_API_URL` emergency override;
2. build-time `VITE_API_URL`;
3. `http://localhost:8000`.

See `GUIDE_KHOI_DONG.md` for ngrok and deployment operations.
