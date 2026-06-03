# Xiaozhi Philosophy AI (小智哲学) 🤖📖

Xiaozhi (Tiểu Trí) là một trợ lý AI thông minh chuyên về **Triết học Mác - Lênin**, được xây dựng dựa trên công nghệ **RAG (Retrieval-Augmented Generation)**. Hệ thống sử dụng mô hình nhúng (Embeddings) chạy hoàn toàn offline bằng HuggingFace và kết hợp sức mạnh phân tích của mô hình Google Gemini để cung cấp những câu trả lời triết học mạch lạc, chính xác và bám sát giáo trình.

---

## 🌟 Tính năng nổi bật
* **Local Embeddings**: Chạy nhúng văn bản cục bộ (`all-MiniLM-L6-v2` / `multilingual-e5-small`) giúp tiết kiệm chi phí API và không bị giới hạn quota.
* **Vector Database**: Sử dụng `ChromaDB` lưu trữ cục bộ, truy xuất tốc độ cao.
* **Fallback thông minh**: Tự động chuyển đổi mô hình dự phòng khi mất kết nối máy chủ tải model.
* **Terminal UI (TUI) đẹp mắt**: Giao diện dòng lệnh tương tác trực quan bằng thư viện `Rich` và `Textual`.
* **REST API**: Tích hợp sẵn FastAPI, dễ dàng kết nối với Web, App hoặc các nền tảng khác.
* **Prompt tối ưu**: Trả lời súc tích, đi thẳng vào vấn đề, từ chối những câu hỏi ngoài lề hoặc không có trong giáo trình để tránh "ảo giác" (hallucination).

---

## 🛠 Cài đặt & Môi trường

### 1. Yêu cầu hệ thống
* Python 3.10 trở lên
* Có kết nối mạng (để tải Model từ HuggingFace lần đầu và gọi Google Gemini API).

### 2. Thiết lập dự án
Clone dự án và di chuyển vào thư mục gốc:
```bash
git clone https://github.com/FinDaHuman/XiaozhiPhilosophyAI.git
cd XiaozhiPhilosophyAI/backend
```

### 3. Tạo môi trường ảo (Virtual Environment)
Khuyến nghị sử dụng môi trường ảo để không xung đột thư viện:
```bash
python -m venv venv
# Kích hoạt trên Windows:
.\venv\Scripts\activate
# Kích hoạt trên Mac/Linux:
source venv/bin/activate
```

### 4. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### 5. Cấu hình biến môi trường (`.env`)
Trong thư mục `backend/`, tạo file `.env` (hoặc sửa đổi file có sẵn) với nội dung:
```ini
# Google AI API Key (Bắt buộc)
GOOGLE_API_KEY=your_google_api_key_here

# Model configuration
GEMINI_MODEL=gemini-2.5-flash-lite
EMBEDDING_MODEL=intfloat/multilingual-e5-small

# Vector DB & RAG config
CHROMA_PERSIST_DIR=chroma_db
CHROMA_COLLECTION=philosophy_docs
CHUNK_SIZE=1200
CHUNK_OVERLAP=200
TOP_K=6
```

---

## 🚀 Hướng dẫn sử dụng

### Bước 1: Nạp dữ liệu (Ingestion)
Trước khi chat, bạn cần nạp các tài liệu (Giáo trình Triết học) vào Cơ sở dữ liệu Vector:
1. Đặt các file tài liệu (`.pdf`, `.docx`, `.txt`) vào thư mục `data/` (ngang hàng với `backend/`).
2. Chạy lệnh nạp dữ liệu:
```bash
python -m app.main ingest
```
*Lưu ý: Bạn có thể thêm cờ `--resume` nếu muốn tiếp tục quá trình nạp bị lỗi giữa chừng.*

### Bước 2: Tương tác với AI
Hệ thống cung cấp 2 chế độ tương tác:

#### 🖥️ Chế độ Terminal (TUI)
Dành cho người dùng muốn chat trực tiếp thông qua cửa sổ dòng lệnh có giao diện trực quan:
```bash
python -m app.main terminal
```

#### 🌐 Chế độ API Server (REST API)
Dành cho nhà phát triển muốn tích hợp Xiaozhi vào ứng dụng khác:
```bash
python -m app.main api
```
- Server sẽ chạy tại: `http://localhost:8000`
- **Tài liệu API (Swagger UI):** Truy cập `http://localhost:8000/docs` để test trực tiếp các endpoint.
- **Endpoint Chat:** `POST /chat`
  ```json
  // Request
  {
    "message": "Nguyên nhân là gì?"
  }
  
  // Response
  {
    "answer": "Nguyên nhân là phạm trù chỉ sự tương tác lẫn nhau..."
  }
  ```

---

## 📝 Cấu trúc thư mục (Tham khảo)
```
XiaozhiPhilosophyAI/
├── backend/
│   ├── app/                # Core logic (RAG pipeline, API, TUI)
│   ├── models/             # Thư mục lưu cục bộ HuggingFace Embeddings
│   ├── chroma_db/          # Cơ sở dữ liệu Vector cục bộ
│   ├── requirements.txt
│   ├── .env
│   └── ...
├── data/                   # Chứa các file tài liệu Triết học để Ingest
└── README.md
```

## 📜 Giấy phép
Dự án được xây dựng cho mục đích học tập và tra cứu Triết học Mác-Lênin.
