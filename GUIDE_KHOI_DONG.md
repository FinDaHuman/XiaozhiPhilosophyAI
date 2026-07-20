# HƯỚNG DẪN KHỞI ĐỘNG LẠI TOÀN BỘ HỆ THỐNG (Lily & Hiro)

> Dùng file này mỗi khi cần bật lại hệ thống (ví dụ: ngày thuyết trình).
> **Đường chính**: chạy `.\start_all.ps1` (1 lệnh, ~3-5 phút). Đường thủ công từng bước ở phần B là dự phòng.
>
> **Thay đổi lớn (20/07/2026)**: browser gọi **Vercel same-origin `/api` proxy**,
> Vercel mới gọi ngrok static domain. Wi-Fi trường/hội trường chặn DNS ngrok sẽ
> không làm hỏng web chat; URL backend vẫn cố định và không cần deploy lại mỗi lần bật tunnel.

---

## Setup ngrok MỘT LẦN DUY NHẤT (nếu chưa làm)

> **ĐÃ LÀM XONG 18/07/2026** — domain: `crumpled-exciting-undertow.ngrok-free.dev`, authtoken đã lưu,
> `NGROK_DOMAIN` đã có trong `.env`, `frontend/vercel.json` đã trỏ proxy đến domain này.
> Phần dưới chỉ để tham khảo nếu làm lại từ đầu.

1. Tạo tài khoản tại https://dashboard.ngrok.com (miễn phí).
2. Dashboard → **Domains** → tạo 1 static domain miễn phí (dạng `xxx.ngrok-free.app` hoặc `xxx.ngrok-free.dev`). Ghi lại.
3. Dashboard → **Your Authtoken** → copy token (**chỉ copy chuỗi token, ĐỪNG copy cả dấu `$` của dòng lệnh mẫu** — đã dính lỗi này 18/07, ngrok báo ERR_NGROK_105).
4. Cài ngrok Windows (https://ngrok.com/download hoặc Microsoft Store) — cần gọi được lệnh `ngrok` từ PowerShell.
5. Chạy 1 lần: `ngrok config add-authtoken <TOKEN>`
6. Thêm dòng sau vào `D:\VsCode\LilyAndHiro\.env`:
   ```
   NGROK_DOMAIN=<domain-cua-ban>
   ```
7. Cập nhật destination `/api/:path*` trong `frontend/vercel.json`, rồi deploy lại Vercel 1 LẦN CUỐI.
   Sau lần này, không bao giờ phải redeploy vì tunnel nữa.

---

## A. Đường chính: 1 lệnh

```powershell
cd D:\VsCode\LilyAndHiro
.\start_all.ps1
```

Script tự làm theo thứ tự: kiểm tra port 8000 trống → bật backend (chờ /health) → bật ngrok
(verify qua Vercel `/api/health`) → bật robot bridge (mcp_pipe) → đánh thức server DongAnh Capital → bật vòng
keep-alive DAC → in khối **READY** với đầy đủ URL.

- Nếu bị chặn script: chạy 1 lần `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
- Script mở thêm 3 cửa sổ (backend, robot, keep-alive) + ngrok — **giữ mở suốt buổi**.
- Tắt tất cả sau buổi: `.\stop_all.ps1`

**Kiểm tra sau khi READY:**
1. Mở https://lily-hiro.vercel.app (Ctrl+F5) → chat thử `Mâu thuẫn biện chứng là gì?` → có `[Slide N]` + ảnh slide.
2. Hỏi robot: `VNINDEX hôm nay thế nào?` → đọc số liệu thật.

---

## B. Đường thủ công (dự phòng khi script trục trặc)

Mở 3 cửa sổ PowerShell (`Win + X` → Terminal, thêm tab `Ctrl + Shift + T`).

### Bước 1 — Backend (cửa sổ 1, GIỮ MỞ)

```powershell
cd D:\VsCode\LilyAndHiro
$env:PYTHONIOENCODING='utf-8'
venv\Scripts\python main.py api
```

Chờ `Uvicorn running on http://0.0.0.0:8000` (lần đầu nạp model 1-2 phút). Kiểm tra ở cửa sổ 3:

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
```

→ `200` + `{"status":"ok"}`.

### Bước 2 — Tunnel ngrok (cửa sổ 2, GIỮ MỞ)

```powershell
ngrok http --url=crumpled-exciting-undertow.ngrok-free.dev 8000
```

URL cố định — không cần copy gì cả. Kiểm tra đúng đường production (cửa sổ 3):

```powershell
Invoke-WebRequest -Uri "https://lily-hiro.vercel.app/api/health" -Headers @{"ngrok-skip-browser-warning"="true"} -UseBasicParsing
```

Không dùng lỗi khi mở trực tiếp `ngrok.com` để kết luận tunnel chết: DNS của
Wi-Fi có thể trả `standard-block.dns.adguard.com` trong khi Vercel proxy vẫn hoạt động.

### Bước 3 — Robot (cửa sổ 3, GIỮ MỞ)

```powershell
cd D:\VsCode\LilyAndHiro\mcp
$env:PYTHONIOENCODING='utf-8'
..\venv\Scripts\python mcp_pipe.py
```

Chờ `Connecting to WebSocket endpoint` + `Started server process`.

> Robot giờ ưu tiên hỏi backend web (bộ não ChromaDB mạnh hơn, persona giọng nói);
> backend tắt thì tự rơi về FAISS local — robot vẫn nói được, chỉ kém sâu hơn.

### Bước 4 — Đánh thức DongAnh Capital

```powershell
Invoke-WebRequest -Uri "https://donganhcapital.onrender.com/api/vnindex?limit=1" -UseBasicParsing -TimeoutSec 120
```

(Server Render free ngủ sau 15 phút — nếu không chạy keep-alive thì thỉnh thoảng gọi lại lệnh này.)

---

## Khẩn cấp giữa buổi: ngrok tunnel/provider thật sự không tới được

Chỉ dùng mục này khi `https://lily-hiro.vercel.app/api/health` lỗi. Việc máy
chiếu không mở trực tiếp được `ngrok.com` không còn ảnh hưởng web production.

1. Bật Cloudflare quick tunnel thay thế (cửa sổ mới):
   ```powershell
   & "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --protocol http2 --url http://localhost:8000
   ```
   Copy URL `https://xxx.trycloudflare.com` trong log.
2. Trên máy chiếu web, mở DevTools (F12) → Console → gõ:
   ```js
   localStorage.setItem('LILY_API_URL', 'https://xxx.trycloudflare.com'); location.reload()
   ```
   → Web lập tức trỏ sang tunnel mới, **KHÔNG cần deploy lại Vercel**.
3. Xoá override khi xong: `localStorage.removeItem('LILY_API_URL'); location.reload()`

---

## Deploy lại Vercel (chỉ khi đổi domain ngrok hoặc sửa code frontend/proxy)

Production không còn bake `VITE_API_URL` vào bundle. Domain backend nằm trong
rewrite same-origin của `frontend/vercel.json`.

```powershell
cd D:\VsCode\LilyAndHiro\frontend
vercel pull --yes --environment production
vercel build --prod --yes
vercel deploy --prebuilt --prod --yes
```

Kiểm tra sau khi deploy:

```powershell
Invoke-WebRequest -Uri "https://lily-hiro.vercel.app/api/health" -UseBasicParsing
```

Kết thúc phải thấy `▲ Aliased https://lily-hiro.vercel.app`.

---

## Sự cố thường gặp

| Triệu chứng | Nguyên nhân | Cách xử lý |
|---|---|---|
| start_all báo port 8000 bị chiếm | Backend cũ còn chạy, HOẶC **dev server DongAnhCapital local** đang chạy port 8000 | Tắt process đó trước (script in sẵn PID). Dev DAC local bind 127.0.0.1 sẽ "cướp" request của Lily |
| ngrok báo lỗi auth | Chưa `config add-authtoken` | Chạy lại bước setup 5 |
| Mở trực tiếp ngrok báo SSL/DNS block | Wi-Fi trả domain về `standard-block.dns.adguard.com` | Không ảnh hưởng production nếu `/api/health` trả 200; browser chỉ gọi Vercel |
| Web chat không phản hồi | Backend tắt / Vercel proxy không tới tunnel | Mở `/api/health`, rồi xem cửa sổ backend + ngrok; Lily vẫn tự fallback từ streaming sang `/chat` |
| Web báo "Bạn hỏi nhanh quá" (429) | Rate limit 20 câu/phút/IP (khách lạ spam) | Bình thường — localhost và robot không bao giờ bị giới hạn |
| Chữ tiếng Việt terminal lỗi/crash | Console cp1252 | Đã có `$env:PYTHONIOENCODING='utf-8'` — đừng bỏ |
| Lily "không tìm thấy thông tin" | Sai chroma_db / chưa ingest tài liệu mới | Xem re-ingest trong `HANDOFF.md` (TẮT backend + XÓA `chroma_db` trước) |
| Robot không kết nối | Token sai/hết hạn trong `.env` | Token mới tại console xiaozhi.me → sửa `MCP_ENDPOINT` → chạy lại mcp_pipe |
| Robot trả lời kiểu cũ (đọc cả ngoặc vuông) | Backend web tắt, đang chạy FAISS bản cũ chưa re-ingest | Bật backend rồi hỏi lại; FAISS cũng đã có persona giọng nói mới |
| Câu "VNINDEX hôm nay" ra số liệu "phiên gần nhất" | Render DAC đang ngủ, robot dùng cache | Chấp nhận được; keep-alive sẽ giữ server thức trong buổi |

---

*File liên quan: `PRESENTATION.md` (kịch bản + checklist ngày D), `HANDOFF.md` (chi tiết kỹ thuật), `todolist.txt` (việc còn lại).*
