# Xiaozhi Philosophy AI Core MVP

## Objective

Build the AI brain for the philosophy robot.

Deliverables:

* Philosophy RAG
* Terminal Chat UI
* FastAPI API
* MCP-ready backend

Not included:

* Website
* Login
* Frontend
* Robot hardware
* Speech-to-Text
* Text-to-Speech

---

# Scope

```text
User
 ↓
Terminal
 ↓
RAG
 ↓
Groq
 ↓
Answer
```

and

```text
Robot MCP
 ↓
FastAPI
 ↓
RAG
 ↓
Groq
 ↓
Answer
```

---

# Deliverable 1: Knowledge Base Pipeline

## Input

Support:

```text
PDF
DOCX
TXT
MD
```

Directory:

```text
data/
```

Example:

```text
data/
├── giao_trinh_triet_hoc.pdf
├── chu_nghia_duy_vat.pdf
├── slide01.pdf
├── slide02.pdf
└── ...
```

---

## Processing

Pipeline:

```text
Load Documents
 ↓
Clean Text
 ↓
Chunk
 ↓
Embed
 ↓
Store
```

---

## Chunk Configuration

```python
chunk_size = 1000
chunk_overlap = 200
```

---

## Embedding Model

Preferred:

```text
Google text-embedding-004
```

Fallback:

```text
all-MiniLM-L6-v2
```

---

## Vector Database

```text
ChromaDB
```

Persist locally:

```text
chroma_db/
```

---

# Deliverable 2: RAG Engine

## Retrieval

```text
Question
 ↓
Embedding
 ↓
Similarity Search
 ↓
Top 5 Chunks
 ↓
Prompt Builder
 ↓
Groq
 ↓
Answer
```

---

## Rules

Assistant must:

* answer in Vietnamese
* prioritize uploaded materials
* avoid hallucination
* state uncertainty if information not found

Example:

```text
Không tìm thấy thông tin liên quan trong cơ sở tri thức hiện tại.
```

---

# Deliverable 3: Terminal Interface

Goal:

Codex CLI style experience.

---

## Commands

```text
/help
/clear
/reload
/stats
/exit
```

---

## UI

Example:

```text
┌──────────────────────────────────────┐
│ Xiaozhi Philosophy AI                │
├──────────────────────────────────────┤
│ User: Triết học là gì?               │
│                                      │
│ AI: Triết học là hệ thống tri thức...│
│                                      │
├──────────────────────────────────────┤
│ >                                    │
└──────────────────────────────────────┘
```

---

## Features

Required:

* conversation history
* markdown rendering
* scrolling
* multiline answers

Optional:

* syntax highlighting
* streaming response

---

# Deliverable 4: FastAPI Backend

## Endpoint

### POST /chat

Request

```json
{
  "message": "Nguyên nhân là gì?"
}
```

Response

```json
{
  "answer": "..."
}
```

---

### GET /health

Response

```json
{
  "status": "ok"
}
```

---

### POST /reload

Purpose:

Reload knowledge base after adding documents.

---

# Deliverable 5: MCP Compatibility

Backend must expose a simple interface.

Example:

```python
answer = rag.ask(question)
```

or

```http
POST /chat
```

No robot-specific code required.

The robot team will handle:

* microphone
* STT
* TTS
* motor control
* MCP orchestration

---

# Recommended Tech Stack

```text
Python 3.11

FastAPI
LangChain
ChromaDB
Groq (llama-3.1-8b-instant)
Textual
python-dotenv
```

---

# Folder Structure

```text
backend/

├── app/
│   ├── rag/
│   │   ├── ingest.py
│   │   ├── retriever.py
│   │   ├── prompts.py
│   │   └── pipeline.py
│   │
│   ├── api/
│   │   └── routes.py
│   │
│   ├── ui/
│   │   └── terminal.py
│   │
│   └── main.py
│
├── data/
├── chroma_db/
├── .env
└── requirements.txt
```

---

# Success Criteria

MVP is complete when:

✅ Upload philosophy PDFs

✅ Build vector database

✅ Ask philosophy questions in terminal

✅ Receive grounded answers

✅ FastAPI endpoint works

✅ Robot team can call API immediately