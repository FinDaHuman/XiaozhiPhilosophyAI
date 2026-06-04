# Xiaozhi Philosophy AI (小智哲学) 🤖📖

Xiaozhi (Tiểu Trí) là một trợ lý AI thông minh chuyên về **Triết học Mác - Lênin**, được xây dựng dựa trên công nghệ **RAG (Retrieval-Augmented Generation)**. Hệ thống cung cấp câu trả lời triết học mạch lạc, chính xác, bám sát giáo trình và có khả năng trích dẫn trực tiếp nguồn slide. Đặc biệt, hệ thống hỗ trợ tích hợp với Robot vật lý thông qua **Model Context Protocol (MCP)**.

---

## 🌟 Tính năng nổi bật

1. **Giao diện Web Tương Tác Cấp Cao (React/Vite)**
   - **Chat Split-Screen:** Vừa trò chuyện với AI, vừa xem slide trích dẫn ngay bên cạnh.
   - **Bài học (Lessons):** Lộ trình học được chia bài bản, liên kết trực tiếp với slide.
   - **Kiểm tra kiến thức (Quiz):** 40 câu hỏi trắc nghiệm có phản hồi giải thích ngay lập tức.
2. **Tích hợp Robot Vật Lý (MCP Server)**
   - Cho phép kết nối phần cứng Robot vật lý với AI thông qua cổng WebSocket bảo mật.
   - Server MCP chạy ẩn và tự động đồng bộ kho tri thức FAISS.
3. **Kiến trúc RAG Đa Lớp (Advanced RAG)**
   - **Local Embeddings:** Sử dụng `multilingual-e5-small` chạy hoàn toàn offline.
   - **Hybrid Search:** Kết hợp Vector Search (ChromaDB) và Keyword Search (BM25) để tăng độ chính xác.
4. **Terminal UI (TUI)**
   - Cung cấp giao diện chat dòng lệnh cực kỳ đẹp mắt và nhanh gọn.

---

## 📁 Cấu trúc dự án

```
XiaozhiPhilosophyAI/
├── app/                        # Core backend FastAPI & RAG ChromaDB
│   ├── rag/                    # RAG pipeline, retriever, prompts
│   ├── api/                    # FastAPI REST endpoints
│   └── ui/                     # Terminal chat UI
├── frontend/                   # React Vite Web Frontend
├── mcp/                        # MCP server (FAISS) kết nối Robot
├── data/                       # Chứa tài liệu nguồn (PDF, DOCX)
├── chroma_db/                  # Vector database chính
├── models/                     # Thư mục cache cho mô hình Local
└── main.py                     # Entry point khởi chạy các dịch vụ
```

---

## 🛠 Cài đặt & Môi trường (Setup)

### 1. Yêu cầu hệ thống
* Python 3.10 trở lên
* Node.js 18+
* Trình duyệt web hiện đại

### 2. Cài đặt Backend
Mở Terminal, di chuyển vào thư mục gốc của dự án:
```bash
# 1. Tạo môi trường ảo (Virtual Environment)
python -m venv venv

# 2. Kích hoạt môi trường ảo
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Cài đặt thư viện Python
pip install -r requirements.txt
```

### 3. Cấu hình biến môi trường (`.env`)
Tạo file `.env` tại thư mục gốc và điền thông tin sau:
```ini
# Groq API Key (Lấy tại: https://console.groq.com/keys)
GROQ_API_KEY=gsk_your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Cấu hình RAG
EMBEDDING_MODEL=intfloat/multilingual-e5-small
CHROMA_PERSIST_DIR=chroma_db
CHROMA_COLLECTION=philosophy_docs

# Cấu hình kết nối Robot
MCP_ENDPOINT=wss://api.xiaozhi.me/mcp/?token=YOUR_ROBOT_TOKEN
```

### 4. Cài đặt Frontend
Mở một Terminal khác:
```bash
cd frontend
npm install
```

### 5. Nạp dữ liệu (Ingestion)
Quét toàn bộ tài liệu trong thư mục `data/` vào cơ sở dữ liệu:
```bash
.\venv\Scripts\activate
python main.py ingest
```

---

## 🚀 Hướng dẫn sử dụng chi tiết

Dự án cung cấp 3 cách chính để tương tác với XiaoZhi.

### Chế độ 1: Sử dụng Giao diện Web (Web UI)
Đây là chế độ đầy đủ tính năng nhất, bao gồm Học, Thi và Chat.

**Bước 1: Chạy Backend API**
Mở Terminal 1:
```bash
.\venv\Scripts\activate
python main.py api
```
*(Backend chạy tại `http://localhost:8000`)*

**Bước 2: Chạy Frontend**
Mở Terminal 2:
```bash
cd frontend
npm run dev
```
*(Truy cập trình duyệt tại `http://localhost:5173`)*

**Tương tác với Robot qua Web:**
Từ trang chủ Web, bạn chỉ cần bấm nút **"Hỏi XiaoZhi ngay"**. Lệnh này sẽ gửi tín hiệu xuống Backend để **tự động khởi chạy kết nối MCP với Robot ở chế độ chạy ngầm**, sau đó chuyển bạn vào giao diện Chat. Bạn có thể vừa chat trên Web, vừa nói chuyện với Robot vật lý cùng một lúc.

---

### Chế độ 2: Chạy độc lập MCP Server cho Robot (Terminal)
Nếu bạn chỉ muốn bật kết nối cho Robot vật lý mà không cần giao diện Web.

**Bước 1: Cập nhật dữ liệu FAISS cho Robot (Chỉ làm lần đầu hoặc khi có dữ liệu mới)**
```bash
.\venv\Scripts\activate
cd mcp
python mcp_rag.py --ingest
```

**Bước 2: Mở cầu nối (Pipe) kết nối Robot lên mạng**
```bash
.\venv\Scripts\activate
cd mcp
python mcp_pipe.py
```
*(Terminal sẽ báo `Started server process: python mcp_rag.py`. Kể từ lúc này, bạn có thể bấm nút trên Robot để bắt đầu hỏi đáp).*

---

### Chế độ 3: Sử dụng Terminal UI (TUI)
Một giao diện Chat cực nhanh và đẹp mắt ngay trong màn hình Terminal của bạn (Dành cho Developer/Hacker).

```bash
.\venv\Scripts\activate
python main.py terminal
```
- Gõ câu hỏi trực tiếp để chat.
- Gõ `clear` để xóa lịch sử trò chuyện.
- Gõ `quit` hoặc `exit` để thoát chương trình.

---

## ⚠️ Xử lý lỗi thường gặp

1. **Lỗi `ModuleNotFoundError` khi chạy API hoặc TUI:**
   - **Nguyên nhân:** Chưa kích hoạt môi trường ảo.
   - **Cách sửa:** Luôn chạy lệnh `.\venv\Scripts\activate` (trên Windows) trước khi chạy bất kỳ lệnh `python` nào.

2. **Lỗi khi chạy `mcp_pipe.py` (Lỗi thư viện `mcp`):**
   - **Nguyên nhân:** Config gọi nhầm file Python của hệ thống thay vì môi trường ảo.
   - **Cách sửa:** Chắc chắn rằng file `mcp/mcp_config.json` có dòng:
     `"command": "../venv/Scripts/python.exe"` (đối với Windows).

3. **Web không hiển thị ảnh Slide:**
   - Đảm bảo các ảnh slide `.jpg` đã được bỏ vào thư mục `frontend/public/slides/`. Nếu thiếu, Web sẽ hiển thị khung hình mờ thông báo "Chưa cập nhật" thay vì lỗi vỡ ảnh.

---
*Dự án phát triển nội bộ cho môn học Triết học Mác-Lênin.*