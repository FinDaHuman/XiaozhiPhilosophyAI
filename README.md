# Lily & Hiro

Lily là trợ giảng AI cho hai môn **Triết học Mác - Lênin (MLN111)** và
**Kinh tế chính trị Mác - Lênin (MLN122/KTCT)**. Hệ thống dùng RAG để trả lời
bám sát giáo trình và slide, đồng thời có kiến thức giới thiệu nền tảng
DongAnh Capital và Hiro. Hiro là cố vấn AI nằm trên `donganhcapital.com`, không
được triển khai trong repository này.

Repository gồm web app React/Vite, API FastAPI, terminal REPL và cầu nối MCP cho
robot XiaoZhi. Các câu trả lời liên quan đầu tư chỉ mang tính tham khảo, không
phải lời khuyên đầu tư.

---

## 🌟 Tính năng nổi bật

1. **Web học tập React/Vite**
   - **Chat Split-Screen:** Vừa trò chuyện với AI, vừa xem slide trích dẫn ngay bên cạnh.
   - 8 bài học, 64 ảnh slide và 100 câu quiz cho hai môn (40 MLN111 + 60 KTCT).
   - Chat SSE có history phía client và tự fallback sang response không streaming.
2. **Hai pipeline RAG dùng chung `data/`**
   - Web/API: ChromaDB + multilingual E5 + BM25 + MultiQuery.
   - Robot fallback: FAISS + TF-IDF, dùng khi backend web không sẵn sàng.
   - Cả hai dùng Groq trước và Gemini làm fallback cho lỗi provider tạm thời.
3. **Robot XiaoZhi qua MCP**
   - `rag_answer` ưu tiên endpoint giọng nói của backend rồi mới fallback FAISS.
   - 7 MCP tools: 4 tools RAG và 3 tools dữ liệu thị trường DongAnh Capital.
4. **Terminal REPL**
   - Chat có markdown, history, reload và thống kê hệ thống.

---

## 📁 Cấu trúc dự án

```text
LilyAndHiro/
├── app/                        # Core backend FastAPI & RAG ChromaDB
│   ├── rag/                    # RAG pipeline, retriever, prompts
│   ├── api/                    # FastAPI REST endpoints
│   └── ui/                     # Terminal chat UI
├── mcp/                        # MCP tools, bridge và FAISS fallback
├── data/                       # Tài liệu nguồn PDF, DOCX và Markdown
├── frontend/                   # React/Vite SPA
├── chroma_db/                  # ChromaDB sinh cục bộ, được gitignore
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

# Gemini fallback (chỉ dùng khi Groq gặp 429, timeout hoặc lỗi 5xx)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash-lite

# Cấu hình RAG
EMBEDDING_MODEL=intfloat/multilingual-e5-small
CHROMA_PERSIST_DIR=chroma_db
CHROMA_COLLECTION=philosophy_docs

# Cấu hình kết nối Robot
MCP_ENDPOINT=wss://api.xiaozhi.me/mcp/?token=YOUR_ROBOT_TOKEN
NGROK_DOMAIN=your-static-domain.ngrok-free.dev
TOP_K=6
```

Để bảo vệ quota free-tier, ứng dụng tắt retry ngầm của Gemini SDK: lỗi 429 không
được gọi lại, còn lỗi máy chủ 5xx chỉ được thử lại đúng một lần.

### 4. Cài đặt Frontend
Mở một Terminal khác:
```bash
cd frontend
npm install
```

### 5. Nạp dữ liệu (Ingestion)
Nạp `data/` cho cả hai store. Chạy lại khi tài liệu nguồn thay đổi:
```bash
.\venv\Scripts\activate
python main.py ingest
cd mcp
python rag_pipeline_faiss.py ingest
```

---

## 🚀 Hướng dẫn sử dụng chi tiết

Dự án cung cấp ba cách chính để tương tác với Lily.

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

Từ trang chủ, chọn **"Hỏi Lily ngay"** để mở chat. Khởi động robot bridge bằng
`.\start_all.ps1`, `POST /api/start-mcp`, hoặc lệnh thủ công ở phần tiếp theo;
nút chat không tự khởi động robot.

---

### Chế độ 2: Chạy độc lập MCP Server cho Robot (Terminal)
Nếu bạn chỉ muốn bật kết nối cho Robot vật lý mà không cần giao diện Web.

**Bước 1: Cập nhật dữ liệu FAISS cho Robot (Chỉ làm lần đầu hoặc khi có dữ liệu mới)**
```bash
.\venv\Scripts\activate
cd mcp
python rag_pipeline_faiss.py ingest
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
- Gõ `/help` để xem lệnh.
- Dùng `/clear`, `/reload`, `/stats` và `/exit` để điều khiển phiên.

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
## Tài liệu liên quan

- `GUIDE_KHOI_DONG.md`: vận hành local, ngrok và Vercel.
- `API_INTEGRATION.md`: contract HTTP, SSE và WebSocket.
- `MCP_INTEGRATION.md`: kiến trúc robot và 7 MCP tools.
- `XIAOZHI_HARDWARE_SETUP.md`: ghép nối phần cứng.
- `PRESENTATION.md`: checklist và kịch bản demo.

*Dự án demo giáo dục nội bộ; dữ liệu thị trường không phải lời khuyên đầu tư.*
