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

## URL hiện tại (18/07/2026)

- Website Lily (Vercel): **https://lily-hiro.vercel.app**
- Tunnel backend: ngrok static domain — **cố định**, xem `NGROK_DOMAIN` trong `.env` (không đổi khi restart, không cần redeploy Vercel)
- Backend local: http://localhost:8000

## Checklist ngày thuyết trình (làm trước 15+ phút)

> **Chi tiết từng bước + xử lý sự cố: xem `GUIDE_KHOI_DONG.md`.**

1. [ ] Chạy `.\start_all.ps1` từ thư mục gốc repo → chờ khối **READY**
   (script tự lo: backend + tunnel ngrok + robot + đánh thức DAC + keep-alive DAC)
2. [ ] Mở https://lily-hiro.vercel.app (Ctrl+F5), chat thử 1 câu triết học + 1 câu KTCT → có trích dẫn slide + ảnh hiện đúng
3. [ ] Test robot bằng giọng nói: 1 câu triết học + `"VNINDEX hôm nay thế nào?"` (câu này đồng thời prime cache số liệu cho robot)
4. [ ] Mở sẵn các tab web: donganhcapital.com (Dashboard, AI Analyst, AI Chat) + website Lily trên Vercel
5. [ ] Đăng nhập sẵn tài khoản Pro/Premium trên donganhcapital.com để demo Hiro
6. [ ] **KHÔNG chạy dev server DongAnhCapital local trong buổi demo** (nó chiếm port 8000, cướp request của Lily — start_all sẽ tự phát hiện và cảnh báo)
7. [ ] Sau buổi: `.\stop_all.ps1`

## Phương án dự phòng

- **ngrok chết / mạng hội trường chặn**: bật cloudflared quick tunnel + repoint web bằng
  `localStorage.setItem('LILY_API_URL', '<URL tunnel mới>')` trong DevTools Console — KHÔNG cần redeploy (chi tiết trong `GUIDE_KHOI_DONG.md` mục "Khẩn cấp giữa buổi").
- **Mất mạng / Render chết**: câu "VNINDEX hôm nay" vẫn trả lời được bằng **số liệu cache phiên gần nhất** (robot tự nói rõ là số liệu gần nhất); các câu 1-2-4 chạy docs tĩnh. Web DAC thay bằng screenshot/video quay sẵn.
- **Robot trục trặc**: chuyển demo Lily sang website (Vercel) hoặc terminal (`venv\Scripts\python main.py terminal`) — cùng một bộ não RAG.
- **Backend Lily chết giữa buổi**: robot vẫn tự trả lời bằng FAISS local (giọng nói vẫn ổn, chỉ kém sâu hơn) — cứ demo tiếp, bật lại backend sau.
- **Hiro hết quota / lỗi**: dùng screenshot hội thoại Hiro chuẩn bị sẵn.
