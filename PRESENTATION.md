# Kịch bản thuyết trình: Lily × Hiro — Từ Triết học đến Đầu tư

> Thiết bị: robot XiaoZhi (Lily) + laptop chiếu web. Thời lượng gợi ý: 12–15 phút.

## Phần 1 — Tái giới thiệu Lily AI (3–4 phút)

**Nói:** "Học kỳ trước, nhóm đã xây dựng Lily — trợ lý AI triết học Mác-Lênin chạy trên robot XiaoZhi. Lily dùng kiến trúc RAG: kiến thức lấy từ giáo trình và slide thật, trả lời có trích dẫn nguồn, không bịa."

**Điểm nhấn kỹ thuật (1 slide):**
- RAG 2 tầng: ChromaDB + embeddings đa ngôn ngữ (web) và FAISS + TF-IDF (robot, nhẹ để phản hồi nhanh)
- LLM: Groq (llama-3.3-70b) — miễn phí, tốc độ cao
- Robot kết nối qua Model Context Protocol (MCP) — chuẩn mở của Anthropic
- Website học tập: chat split-screen xem slide, bài học, quiz 40 câu

**Demo 1 (robot):** bấm nút, hỏi Lily:
> "Lily ơi, mâu thuẫn biện chứng là gì?"

→ Lily trả lời kèm trích dẫn slide. Nhắc khán giả để ý câu trả lời có [Slide X].

## Phần 2 — Giới thiệu donganhcapital.com (4–5 phút)

**Nói:** "Từ nền tảng đó, dự án mới của mình là DongAnh Capital — nền tảng phân tích chứng khoán Việt Nam bằng AI, đang chạy thật tại donganhcapital.com."

**Demo web theo thứ tự (mở sẵn tab):**
1. **Dashboard** — VNINDEX + VN30F1M realtime
2. **AI Analyst** — tín hiệu breakout hằng ngày do model ML tạo lúc 15:02 sau phiên
3. **Pro Signals / BCD Signals** — model xếp hạng LTR và model bắt đáy B-C-D
4. **News** — tin CafeF + tin vĩ mô thế giới
5. **AI Chat** — "Và đây là Hiro — AI cố vấn đầu tư của nền tảng. Hỏi Hiro về một mã cổ phiếu, Hiro tự tra giá thật, tín hiệu thật, tin thật rồi mới trả lời."

**Demo Hiro (tùy thời gian):** gõ "Nhận định về FPT hôm nay?" → chỉ cho khán giả thấy Hiro trích giá + tín hiệu thật.

## Phần 3 — Lily nói về Hiro và DongAnh Capital (4–5 phút)

**Nói:** "Điều thú vị: Lily giờ cũng đã 'biết' về DongAnh Capital. Kho tri thức của Lily được bổ sung tài liệu về nền tảng, và Lily có thêm tool lấy dữ liệu thị trường trực tiếp từ API của donganhcapital.com."

**Demo 2 (robot) — hỏi lần lượt:**
1. > "Lily ơi, donganhcapital.com là gì?"
   → Lily giới thiệu nền tảng (từ docs đã ingest)
2. > "Tín hiệu AI của DongAnh Capital hoạt động thế nào?"
   → Lily nói về 3 model Breakout / LTR / BCD + disclaimer
3. > "VNINDEX hôm nay thế nào?"
   → Lily gọi tool live `dac_vnindex` đọc số liệu thật ⭐ điểm nhấn
4. > "Mình muốn được tư vấn sâu về một mã cổ phiếu thì hỏi ai?"
   → Lily giới thiệu Hiro: "nhà cố vấn đầu tư trên tab AI Chat của donganhcapital.com" — khép vòng câu chuyện

**Chốt:** "Một hệ sinh thái hai AI: Lily — người bạn triết học rèn tư duy, Hiro — nhà cố vấn thực chiến trên thị trường. Cùng một triết lý thiết kế: AI phải trả lời dựa trên dữ liệu thật và luôn trung thực về giới hạn của mình."

---

## URL hiện tại (17/07/2026)

- Website Lily (Vercel): **https://lily-hiro.vercel.app**
- Tunnel backend: https://induction-aged-sin-logs.trycloudflare.com (đổi mỗi lần chạy lại cloudflared)
- Backend local: http://localhost:8000

## Checklist ngày thuyết trình (làm trước 15 phút)

> **Hướng dẫn từng bước chi tiết (cd vào đâu, chạy gì, kiểm tra thế nào): xem `GUIDE_KHOI_DONG.md`.**

1. [ ] Đánh thức backend DAC (Render free ngủ sau 15 phút):
   `curl https://donganhcapital.onrender.com/api/health` — đợi tới khi trả `ok`
2. [ ] Bật backend Lily (từ thư mục gốc repo): `venv\Scripts\python main.py api` (đợi log "Uvicorn running")
3. [ ] Bật tunnel: `& "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --protocol http2 --url http://localhost:8000` — chép URL `*.trycloudflare.com` mới trong log
   (mạng này chặn QUIC/UDP nên bắt buộc `--protocol http2`)
4. [ ] Nếu URL tunnel đổi (luôn đổi sau khi restart): redeploy frontend với URL mới:
   `cd frontend` rồi build local + prebuilt (KHÔNG dùng --build-env, nó không bake VITE_API_URL):
   `vercel pull --yes --environment production`
   `$env:VITE_API_URL='<URL tunnel mới>'; vercel build --prod --yes`
   `vercel deploy --prebuilt --prod --yes` (~2 phút)
5. [ ] Bật cầu robot: `cd mcp` rồi `..\venv\Scripts\python mcp_pipe.py` — chờ log "Started server process"; nếu lỗi 401/403 → token hết hạn, lấy token mới tại console xiaozhi.me và cập nhật `MCP_ENDPOINT` trong `.env`
6. [ ] Test robot 1 câu triết học + 1 câu "VNINDEX hôm nay thế nào?"
7. [ ] Mở sẵn các tab web: donganhcapital.com (Dashboard, AI Analyst, AI Chat) + website Lily trên Vercel
8. [ ] Đăng nhập sẵn tài khoản Pro/Premium trên donganhcapital.com để demo Hiro

## Phương án dự phòng

- **Mất mạng / Render chết**: bỏ câu hỏi số 3 (live), các câu 1-2-4 vẫn chạy vì dùng docs tĩnh trong FAISS local. Web DAC thay bằng screenshot/video quay sẵn.
- **Robot trục trặc**: chuyển demo Lily sang website (Vercel) hoặc terminal (`venv\Scripts\python main.py terminal`) — cùng một bộ não RAG.
- **Hiro hết quota / lỗi**: dùng screenshot hội thoại Hiro chuẩn bị sẵn.
