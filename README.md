# Xiaozhi Philosophy AI (小智哲学) 🤖📖

Xiaozhi (Tiểu Trí) là một trợ lý AI thông minh chuyên về **Triết học Mác - Lênin**, được xây dựng dựa trên công nghệ **RAG (Retrieval-Augmented Generation)**. Hệ thống sử dụng mô hình nhúng (Embeddings) chạy hoàn toàn offline bằng HuggingFace và kết hợp sức mạnh phân tích của **Groq API** (LLaMA) để cung cấp những câu trả lời triết học mạch lạc, chính xác và bám sát giáo trình.

---

## 🌟 Tính năng nổi bật

* **Local Embeddings**: Chạy nhúng văn bản cục bộ (`multilingual-e5-small`) giúp tiết kiệm chi phí API và không bị giới hạn quota.
* **Vector Database**: Sử dụng `ChromaDB` lưu trữ cục bộ, truy xuất tốc độ cao.
* **Groq LLM**: Sử dụng Groq API (`llama-3.1-8b-instant`) với tốc độ phản hồi cực nhanh.
* **MCP Integration**: Tích hợp sẵn MCP server để kết nối với robot Xiaozhi.
* **Terminal UI (TUI) đẹp mắt**: Giao diện dòng lệnh tương tác trực quan bằng thư viện `Rich`.
* **REST API**: Tích hợp sẵn FastAPI, dễ dàng kết nối với Web, App hoặc các nền tảng khác.
* **Prompt tối ưu**: Trả lời súc tích, đi thẳng vào vấn đề, tránh "ảo giác" (hallucination).

---

## 📁 Cấu trúc dự án

```
XiaozhiPhilosophyAI/
├── backend/                    # Core backend (ChromaDB + Groq)
│   ├── app/
│   │   ├── rag/                # RAG pipeline, retriever, embeddings
│   │   ├── api/                # FastAPI REST endpoints
│   │   └── ui/                 # Terminal chat UI
│   ├── chroma_db/              # Vector database (persistent)
│   ├── models/                 # HuggingFace embeddings cache
│   ├── requirements.txt
│   └── .env
├── mcp/                        # MCP server (FAISS + Groq)
│   ├── mcp_rag.py              # MCP tool server (rag_search, rag_answer, etc.)
│   ├── mcp_pipe.py             # WebSocket ↔ stdio bridge
│   ├── rag_pipeline_faiss.py   # Lightweight FAISS + TF-IDF pipeline
│   └── mcp_config.json
├── data/                       # Source documents for both pipelines
├── MCP_INTEGRATION.md          # MCP integration guide
└── README.md
```

---

## 🛠 Cài đặt & Môi trường

### 1. Yêu cầu hệ thống
* Python 3.10 trở lên
* Có kết nối mạng (để tải Model từ HuggingFace lần đầu và gọi Groq API).

### 2. Thiết lập dự án
Clone dự án và di chuyển vào thư mục gốc:
```bash
git clone https://github.com/FinDaHuman/XiaozhiPhilosophyAI.git
cd XiaozhiPhilosophyAI/backend
```

### 3. Tạo môi trường ảo (Virtual Environment)
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 4. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### 5. Cấu hình biến môi trường (`.env`)
Trong thư mục `backend/`, tạo file `.env`:
```ini
# Groq API Key (Bắt buộc)
# Lấy tại: https://console.groq.com/keys
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant

# Embedding model (chạy local, không cần API key)
EMBEDDING_MODEL=intfloat/multilingual-e5-small

# HuggingFace Cache
HF_HOME=./models

# Vector DB & RAG config
CHROMA_PERSIST_DIR=chroma_db
CHROMA_COLLECTION=philosophy_docs
CHUNK_SIZE=1200
CHUNK_OVERLAP=200
TOP_K=6

# Data directory
DATA_DIR=../data
```

---

## 🚀 Hướng dẫn sử dụng

### Bước 1: Nạp dữ liệu (Ingestion)
Đặt các file tài liệu (`.pdf`, `.docx`, `.txt`) vào thư mục `data/`, sau đó:
```bash
python main.py ingest
```
*Thêm `--resume` để tiếp tục quá trình nạp bị lỗi giữa chừng.*

### Bước 2: Tương tác với AI

#### 🖥️ Chế độ Terminal (TUI)
```bash
python main.py terminal
```

#### 🌐 Chế độ API Server
```bash
python main.py api
```
- Server: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- Chat endpoint: `POST /chat`
  ```json
  { "message": "Mâu thuẫn biện chứng là gì?" }
  ```

---

## 🤖 MCP Integration (Robot Xiaozhi)

Thư mục `mcp/` chứa MCP server dùng pipeline nhẹ (FAISS + TF-IDF + Groq) để kết nối trực tiếp với robot Xiaozhi qua WebSocket.

```bash
cd mcp
python rag_pipeline_faiss.py ingest    # Tạo FAISS index
python mcp_pipe.py                     # Kết nối robot
```

Xem chi tiết tại [MCP_INTEGRATION.md](MCP_INTEGRATION.md).

---

## 📜 Giấy phép
Dự án được xây dựng cho mục đích học tập và tra cứu Triết học Mác-Lênin.
