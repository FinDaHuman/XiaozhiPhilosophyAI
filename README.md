# Xiaozhi Philosophy AI (小智哲学) 🤖📖

Xiaozhi (Tiểu Trí) là một trợ lý AI thông minh chuyên về **Triết học Mác - Lênin**, được xây dựng dựa trên công nghệ **RAG (Retrieval-Augmented Generation)**. Hệ thống sử dụng mô hình nhúng (Embeddings) chạy hoàn toàn offline bằng HuggingFace và kết hợp sức mạnh phân tích của **Groq API** (LLaMA) để cung cấp những câu trả lời triết học mạch lạc, chính xác và bám sát giáo trình.

---

## 🌟 Tính năng nổi bật

* **Giao diện Web Trực Quan**: Web App chia đôi màn hình (Split Screen) hiện đại, tự động hiển thị Slide tham chiếu ngay bên cạnh nội dung chat.
* **Local Embeddings**: Chạy nhúng văn bản cục bộ (`multilingual-e5-small`) giúp tiết kiệm chi phí API và không bị giới hạn quota.
* **Vector Database**: Sử dụng `ChromaDB` lưu trữ cục bộ, truy xuất tốc độ cao.
* **Groq LLM**: Sử dụng Groq API (`llama-3.3-70b-versatile`) với tốc độ phản hồi cực nhanh và thông minh.
* **Terminal UI (TUI) đẹp mắt**: Giao diện dòng lệnh tương tác trực quan bằng thư viện `Rich`.
* **REST API**: Tích hợp sẵn FastAPI, dễ dàng kết nối với Web, App hoặc các nền tảng khác.

---

## 📁 Cấu trúc dự án

```
XiaozhiPhilosophyAI/
├── app/                        # Core backend (ChromaDB + Groq)
│   ├── rag/                    # RAG pipeline, retriever, embeddings
│   ├── api/                    # FastAPI REST endpoints
│   └── ui/                     # Terminal chat UI
├── frontend/                   # React Vite Web Frontend (UI)
├── chroma_db/                  # Vector database (persistent)
├── models/                     # HuggingFace embeddings cache
├── mcp/                        # MCP server (FAISS + Groq)
├── data/                       # Source documents cho RAG
├── main.py                     # Entry point (API, TUI, Ingest)
├── requirements.txt
└── .env
```

---

## 🛠 Cài đặt & Môi trường

### 1. Yêu cầu hệ thống
* Python 3.10 trở lên
* Node.js 18+ (để chạy Web frontend)
* Có kết nối mạng (để tải Model từ HuggingFace lần đầu và gọi Groq API).

### 2. Thiết lập dự án
Clone dự án và di chuyển vào thư mục gốc:
```bash
git clone https://github.com/FinDaHuman/XiaozhiPhilosophyAI.git
cd XiaozhiPhilosophyAI
```

### 3. Cài đặt Backend (Python)
Cần tạo môi trường ảo (virtual environment) để tránh xung đột thư viện:

```bash
# 1. Tạo môi trường ảo
python -m venv venv

# 2. Kích hoạt môi trường ảo (BẮT BUỘC TRƯỚC KHI CHẠY CODE)
# Trên Windows:
.\venv\Scripts\activate
# Trên Mac/Linux:
source venv/bin/activate

# 3. Cài đặt thư viện
pip install -r requirements.txt
```

### 4. Cấu hình biến môi trường (`.env`)
Trong thư mục gốc dự án, tạo file `.env`:
```ini
# Groq API Key (Bắt buộc)
# Lấy tại: https://console.groq.com/keys
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Embedding model (chạy local, không cần API key)
EMBEDDING_MODEL=intfloat/multilingual-e5-small

# Vector DB & RAG config
CHROMA_PERSIST_DIR=chroma_db
CHROMA_COLLECTION=philosophy_docs
CHUNK_SIZE=1200
CHUNK_OVERLAP=200
TOP_K=3
```

### 5. Nạp dữ liệu (Ingestion)
Đặt các file tài liệu (`.pdf`, `.docx`, `.txt`) vào thư mục `data/` (và ảnh slide vào `frontend/public/slides/`), sau đó chạy lệnh để vector hóa tài liệu:
```bash
# Nhớ kích hoạt venv trước khi chạy: .\venv\Scripts\activate
python main.py ingest
```

---

## 🚀 Hướng dẫn sử dụng

Bạn có 3 cách để tương tác với XiaoZhi: Web UI, API, hoặc Terminal UI (TUI). 
**Lưu ý: Luôn kích hoạt môi trường ảo (`.\venv\Scripts\activate`) ở mỗi terminal chạy Backend.**

### Cách 1: Chạy giao diện Web (Khuyên dùng)
Bạn cần chạy song song cả Backend API và Frontend. Mở **2 cửa sổ Terminal**:

**Terminal 1 (Backend API):**
```bash
.\venv\Scripts\activate
python main.py api
```
*(Server sẽ chạy tại `http://localhost:8000`)*

**Terminal 2 (Frontend Web):**
```bash
cd frontend
npm install   # Chỉ chạy lần đầu
npm run dev
```
*(Web sẽ chạy tại `http://localhost:5173`. Mở link này trên trình duyệt để sử dụng.)*

---

### Cách 2: Chạy chế độ Terminal UI (TUI)
Nếu bạn thích dùng dòng lệnh, XiaoZhi có một giao diện chat trực quan ngay trên terminal:
```bash
.\venv\Scripts\activate
python main.py terminal
```
Gõ câu hỏi để chat với AI. Gõ `quit` hoặc `exit` để thoát.

---

### Cách 3: Chạy chế độ API Server (Dành cho Developer)
Để cung cấp REST API cho các ứng dụng khác kết nối vào:
```bash
.\venv\Scripts\activate
python main.py api
```
- API Server: `http://localhost:8000`
- Swagger UI (Tài liệu API): `http://localhost:8000/docs`
- Endpoint chat: `POST http://localhost:8000/chat`
  ```json
  { "message": "Mâu thuẫn biện chứng là gì?" }
  ```

---

## 📜 Giấy phép
Dự án được xây dựng cho mục đích học tập và tra cứu Triết học Mác-Lênin.
