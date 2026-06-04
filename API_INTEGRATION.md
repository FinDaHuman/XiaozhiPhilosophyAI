# Tích hợp API Xiaozhi Philosophy AI

Tài liệu này cung cấp hướng dẫn nhanh các Endpoints (điểm cuối) REST API của hệ thống Xiaozhi để đội ngũ Front-end/Leader có thể tích hợp robot vào Web, App hoặc bất kỳ nền tảng nào một cách nhanh chóng.

---

## 1. Chat với AI (Đặt câu hỏi Triết học)

**Endpoint:** `POST /chat`

Gửi câu hỏi của người dùng tới hệ thống RAG để AI xử lý và trả về câu trả lời.

### Request Body (JSON)
```json
{
  "message": "Nguyên nhân là gì?"
}
```

### Response Thành công (200 OK)
```json
{
  "answer": "Nguyên nhân là phạm trù chỉ sự tương tác lẫn nhau giữa các mặt trong một sự vật, hiện tượng hoặc giữa các sự vật, hiện tượng với nhau gây nên những biến đổi nhất định."
}
```

### Response Lỗi (Ví dụ 400 Bad Request)
```json
{
  "detail": "Message cannot be empty"
}
```

---

## 2. Kiểm tra trạng thái máy chủ (Health Check)

**Endpoint:** `GET /health`

Sử dụng để ping xem API server có đang hoạt động bình thường hay không (thích hợp cho cơ chế load balancing hoặc health monitor).

### Request
```http
GET /health HTTP/1.1
Host: localhost:8000
```

### Response Thành công (200 OK)
```json
{
  "status": "ok"
}
```

---

## 3. Xem thống kê (Stats)

**Endpoint:** `GET /stats`

Kiểm tra trạng thái của cơ sở dữ liệu Vector và Embeddings.

### Response Thành công (200 OK)
```json
{
  "vector_store": {
    "collection_name": "philosophy_docs",
    "document_count": 798,
    "persist_directory": "chroma_db",
    "embedding_model": "intfloat/multilingual-e5-small"
  }
}
```

---

## 4. Cập nhật lại Cơ sở tri thức (Reload)

**Endpoint:** `POST /reload`

Nếu có tài liệu mới được thêm vào thư mục `data/` và bạn đã chạy xong lệnh ingest, có thể gọi API này để server tải lại bộ dữ liệu mới mà không cần tắt/bật lại server.

### Response Thành công (200 OK)
```json
{
  "status": "success",
  "stats": {
    "document_count": 800
  }
}
```

---

*Lưu ý: Bạn có thể xem và test thử giao diện API tương tác chuẩn OpenAPI (Swagger) tại địa chỉ: `http://localhost:8000/docs` khi server đang chạy.*
