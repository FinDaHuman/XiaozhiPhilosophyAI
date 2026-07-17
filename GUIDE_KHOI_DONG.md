# HƯỚNG DẪN KHỞI ĐỘNG LẠI TOÀN BỘ HỆ THỐNG (Lily & Hiro)

> Dùng file này mỗi khi máy đã tắt backend/tunnel và cần bật lại (ví dụ: ngày thuyết trình).
> Tổng thời gian: ~10-15 phút. Làm **đúng thứ tự** từ Bước 1 → 6.
>
> **Quy tắc quan trọng nhất**: URL tunnel Cloudflare **ĐỔI MỖI LẦN chạy lại** cloudflared,
> và URL đó được "nướng" vào web lúc build → **đổi tunnel là BẮT BUỘC deploy lại Vercel** (Bước 4).

---

## Chuẩn bị: mở 3 cửa sổ PowerShell

Bạn cần **3 cửa sổ PowerShell riêng** (backend, tunnel, lệnh phụ). Hai cửa sổ đầu phải
**giữ mở suốt buổi thuyết trình** — đóng cửa sổ là chết backend/tunnel.

Mở PowerShell: bấm `Win + X` → chọn "Terminal" (mở thêm tab bằng `Ctrl + Shift + T`).

---

## Bước 1 — Bật backend (cửa sổ 1, GIỮ MỞ)

```powershell
cd D:\VsCode\LilyAndHiro
$env:PYTHONIOENCODING='utf-8'
venv\Scripts\python main.py api
```

- Chờ đến khi thấy dòng kiểu `Uvicorn running on http://0.0.0.0:8000` (lần đầu nạp model embedding có thể mất 1-2 phút).
- **Không đóng cửa sổ này.**

**Kiểm tra** (chạy ở cửa sổ 3):

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
```

→ Phải thấy `StatusCode : 200` và `{"status":"ok"}`. Chưa thấy thì chờ thêm 30 giây rồi thử lại.

---

## Bước 2 — Bật tunnel Cloudflare (cửa sổ 2, GIỮ MỞ)

```powershell
& "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --protocol http2 --url http://localhost:8000
```

- **BẮT BUỘC có `--protocol http2`** — mạng nhà chặn QUIC/UDP, thiếu flag này tunnel sẽ chết với lỗi "exit 58".
- Trong log sẽ hiện URL dạng:

```
https://xxxx-yyyy-zzzz-wwww.trycloudflare.com
```

→ **COPY URL này lại** — cần cho Bước 3 và 4. (URL mỗi lần chạy một khác.)
- **Không đóng cửa sổ này.**

---

## Bước 3 — Kiểm tra tunnel thông tới backend (cửa sổ 3)

Thay `<URL-TUNNEL>` bằng URL vừa copy:

```powershell
Invoke-WebRequest -Uri "<URL-TUNNEL>/health" -UseBasicParsing
```

→ Phải thấy `200` + `{"status":"ok"}`.

> Nếu lỗi "error 1033" hoặc không kết nối được: **bình thường trong ~30 giây đầu** sau khi
> tunnel bật (DNS đang lan truyền). Chờ 30 giây, thử lại. Quá 2 phút vẫn lỗi → xem mục Sự cố cuối file.

---

## Bước 4 — Deploy lại web Vercel với URL tunnel mới (cửa sổ 3)

> **CẢNH BÁO**: KHÔNG dùng `vercel deploy --build-env VITE_API_URL=...` — lệnh đó
> **âm thầm không nướng URL vào web** (đã dính lỗi này 17/07/2026, web public không chat được).
> Làm đúng 4 lệnh dưới đây (build trên máy rồi đẩy lên).

Thay `<URL-TUNNEL>` bằng URL ở Bước 2 (giữ nguyên dấu nháy đơn):

```powershell
cd D:\VsCode\LilyAndHiro\frontend
vercel pull --yes --environment production
$env:VITE_API_URL='<URL-TUNNEL>'
vercel build --prod --yes
vercel deploy --prebuilt --prod --yes
```

- `vercel build` mất ~30 giây, `vercel deploy` mất ~1-2 phút.
- Kết thúc phải thấy dòng `▲ Aliased https://lily-hiro.vercel.app`.

**Kiểm tra URL đã được nướng đúng** (chạy ngay sau `vercel build`, trước khi deploy cũng được):

```powershell
Select-String -Path .vercel\output\static\assets\index-*.js -Pattern "trycloudflare" -List | Select-Object -First 1
```

→ Phải có kết quả (tên file .js hiện ra). Không có kết quả = env chưa ăn, chạy lại từ dòng `$env:VITE_API_URL=...`.

---

## Bước 5 — Kiểm tra web hoàn chỉnh

1. Mở trình duyệt: **https://lily-hiro.vercel.app** (Ctrl+F5 để bỏ cache).
2. Vào tab **Chat**, hỏi: `Mâu thuẫn biện chứng là gì?`
   → Lily trả lời + panel bên phải hiện ảnh slide (trích dẫn `[Slide N]`).
3. Hỏi thêm: `Độc quyền nhà nước là gì?` → trả lời có `[Slide KTCT N]`, ảnh deck KTCT hiện đúng.
4. Nếu chat báo lỗi/không phản hồi → web đang trỏ tunnel cũ hoặc tunnel chết → làm lại Bước 3-4.

---

## Bước 6 — Bật robot

> Token đã điền sẵn trong `.env` (17/07/2026, hạn tới ~2027) — bình thường không cần sửa gì.
> Nếu robot báo lỗi 401/403: lấy token mới tại console xiaozhi.me, sửa dòng `MCP_ENDPOINT=` trong `D:\VsCode\LilyAndHiro\.env`.

1. Chạy (cửa sổ 3 hoặc mở cửa sổ 4, GIỮ MỞ):

```powershell
cd D:\VsCode\LilyAndHiro\mcp
$env:PYTHONIOENCODING='utf-8'
..\venv\Scripts\python mcp_pipe.py
```

   Chờ log `Connecting to WebSocket endpoint` + `Started server process` — không thấy lỗi là đã nối.

2. Test với robot 4 câu:
   - 1 câu triết học: *"Mâu thuẫn biện chứng là gì?"*
   - 1 câu KTCT: *"Độc quyền nhà nước là gì?"*
   - 1 câu live data: *"VNINDEX hôm nay thế nào?"*
   - 1 câu dẫn tới Hiro: *"Tôi muốn được tư vấn đầu tư cổ phiếu thì sao?"*

---

## Trước giờ thuyết trình (thêm ~5 phút)

- **Đánh thức server DongAnh Capital** (Render free ngủ sau 15 phút không dùng):
  mở https://donganhcapital.com và bấm vài tab, hoặc:

  ```powershell
  Invoke-WebRequest -Uri "https://donganhcapital.onrender.com/api/market-status" -UseBasicParsing -TimeoutSec 120
  ```

  (lần đầu có thể mất 30-60 giây — server đang thức dậy, cứ chờ.)
- Đăng nhập tài khoản Pro trên donganhcapital.com sẵn.
- Mở sẵn tab https://lily-hiro.vercel.app.
- Chạy thử kịch bản trong `PRESENTATION.md` một lượt.

---

## Thứ tự TẮT sau buổi thuyết trình

Bấm `Ctrl + C` trong từng cửa sổ (thứ tự nào cũng được): robot (mcp_pipe) → tunnel → backend.
Không cần deploy lại gì khi tắt. Lần bật sau quay lại Bước 1.

---

## Sự cố thường gặp

| Triệu chứng | Nguyên nhân | Cách xử lý |
|---|---|---|
| Tunnel chết ngay, log có "exit 58" / QUIC timeout | Thiếu `--protocol http2` | Chạy lại đúng lệnh Bước 2 |
| "error 1033" khi mở URL tunnel | DNS chưa lan truyền | Chờ 30-60 giây rồi thử lại |
| Web chat không phản hồi | Web đang trỏ tunnel cũ | Làm lại Bước 3 → 4 |
| Backend báo port 8000 đang bận | Backend cũ còn chạy ngầm | `Get-NetTCPConnection -LocalPort 8000 -State Listen` xem PID, rồi `Stop-Process -Id <PID> -Force`, chạy lại Bước 1 |
| Chữ tiếng Việt trong terminal bị lỗi/crash | Console Windows mã hóa cp1252 | Đã có `$env:PYTHONIOENCODING='utf-8'` trong lệnh — đừng bỏ dòng đó |
| `vercel` báo chưa đăng nhập | Hết phiên CLI | `vercel login` (tài khoản findahuman) rồi làm lại Bước 4 |
| Lily trả lời "không tìm thấy thông tin" | Sai chroma_db / vừa thêm tài liệu chưa ingest | Xem mục re-ingest trong `HANDOFF.md` (nhớ: TẮT backend + XÓA thư mục `chroma_db` trước khi ingest lại) |
| Robot không kết nối | Token sai/hết hạn trong `.env` | Lấy token mới ở console xiaozhi.me, sửa `.env`, chạy lại mcp_pipe |

---

*File liên quan: `PRESENTATION.md` (kịch bản), `HANDOFF.md` (chi tiết kỹ thuật), `todolist.txt` (việc còn lại).*
