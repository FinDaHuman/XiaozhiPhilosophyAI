# HANDOFF — Lily & Hiro (cập nhật 18/07/2026)

> File bàn giao cho session/người kế tiếp: mọi thứ đã làm, đang chạy, chưa làm, và các bẫy cần né.
> Xem thêm: `todolist.txt` (việc còn chờ), `PRESENTATION.md` (kịch bản + checklist ngày D).

## 1. Mục tiêu project

Buổi thuyết trình dùng robot phần cứng **XiaoZhi** chạy AI **"Lily"** để:
1. Tái giới thiệu Lily AI (RAG triết học Mác-Lênin, repo gốc: `github.com/FinDaHuman/XiaozhiPhilosophyAI`)
2. Giới thiệu **donganhcapital.com** (repo: `D:\VsCode\DongAnhCapital`, backend Render + frontend Vercel riêng)
3. Hỏi Lily về DAC — Lily gọi chatbot của donganhcapital.com là **Hiro (ひろ)**, "nhà cố vấn đầu tư chứng khoán"

Quyết định đã chốt với user:
- Backend Lily chạy **local + Cloudflare tunnel**; frontend deploy Vercel
- Persona đổi Xiaozhi → Lily; **KHÔNG sửa repo DongAnhCapital** (tên Hiro chỉ nằm trong docs/prompt của Lily)
- Có MCP tool live-data gọi API public DAC

## 2. Kiến trúc (repo này — D:\VsCode\LilyAndHiro)

- **2 pipeline RAG độc lập, cùng đọc `data/`**:
  - `app/rag/` — ChromaDB + e5-small (HuggingFace) + Groq→Gemini fallback → web/API/terminal (`main.py api|terminal|ingest`). Hiện: **1579 chunks / 67 docs**
  - `mcp/` — FAISS + TF-IDF + Groq→Gemini fallback → robot qua `mcp/mcp_pipe.py` (WebSocket bridge → `wss://api.xiaozhi.me`). Hiện: **1470 chunks / 5 docs**
- **Slide-priority**: `retriever.py` + `prompts.py` ưu tiên chunk có `source` bắt đầu bằng `"slide"`. `ingest.py` split mọi file `Slide*_OCR.md` theo header `## [Slide <label>]` → source `"Slide 12"` / `"Slide KTCT 5"`
- **MCP robot tools** (`mcp/mcp_rag.py`): `rag_search/answer/reindex/status` + 3 tool live DAC: `dac_vnindex`, `dac_ai_signals_today`, `dac_market_movers` (timeout 12s; **có cache**: thành công thì lưu `mcp/.dac_cache.json`, API chết thì trả "so lieu phien gan nhat" thay vì chỉ xin lỗi; `DAC_API` env override được để test outage)
- **Chuỗi fallback robot (18/07)**: XiaoZhi → mcp_pipe → mcp_rag `rag_answer` → **thử backend web trước** (probe `/health` 2s → POST `/chat/robot` timeout 45s, persona giọng nói, retriever ChromaDB) → lỗi thì rơi về FAISS local. Trong cả hai pipeline, generation thử Groq trước rồi chuyển `gemini-2.5-flash-lite` khi Groq gặp 429/timeout/5xx; prompt FAISS cũng đã voice-hoá, max_tokens 300. Để giữ quota free-tier, Groq không tự retry, Gemini 429 không retry và Gemini 5xx chỉ retry một lần. `LILY_WEB_BACKEND` env override được.
- **Endpoints backend** (`app/api/routes.py`): `POST /chat` (nhận thêm `history` optional — absent = shared history cũ), `POST /chat/stream` (SSE, token JSON-wrapped, frontend tự fallback `/chat`), `POST /chat/robot` (voice mode, stateless), rate limit 20 req/60s/IP cho cả 3 (localhost miễn trừ — robot không bao giờ bị chặn). `/chat` + `/chat/robot` chạy trong threadpool (web + robot song song không nghẽn).
- **Router/retriever**: heuristic trước (marker câu hỏi/chào, >50 ký tự), chỉ câu mơ hồ mới gọi router LLM. MultiQuery dùng Groq 8B fail-fast; nếu lỗi thì tự hạ xuống vector+BM25 để Gemini vẫn nhận được context.
- **Frontend** (React/Vite): 2 môn học qua `src/data/subjects.js` (nguồn dữ liệu duy nhất). API base qua `src/config.js`: ưu tiên `localStorage.LILY_API_URL` (khẩn cấp) → `VITE_API_URL` (bake lúc build = ngrok domain cố định) → localhost. Mọi call qua `apiFetch()` (tự gắn header `ngrok-skip-browser-warning`). ChatPage: streaming SSE + gửi 3 cặp history cuối.

## 3. Đã làm trong session này

### Đợt 1 — Hồi sinh hệ thống + tích hợp DAC
- Clone repo (nặng ~150MB vì ảnh slide — cần shallow clone + timeout dài), venv `venv/` bằng `py -3.11`, cài deps root + mcp
- Đổi persona Xiaozhi → Lily: `app/rag/prompts.py`, `mcp/rag_pipeline_faiss.py` (2 chỗ), toàn bộ frontend, `main.py`, `app/ui/terminal.py`, title `index.html`
- Soạn `data/DongAnhCapital_KnowledgeBase.md` (giới thiệu DAC, các tab, 3 model AI, giá gói, section Hiro, disclaimer, Q&A khớp câu hỏi demo)
- Prompt rules mới: trích `[DongAnhCapital]`, giới thiệu Hiro khi hỏi tư vấn cổ phiếu, không cam kết lợi nhuận
- 3 MCP tool live DAC (đã test thật, hoạt động)
- `.env` tạo từ key Groq tại `C:\Users\namet\Downloads\key.txt` (56 ký tự, không hiển thị ra console); `MCP_ENDPOINT` còn là placeholder
- Fix frontend hardcode `localhost:8000` → `src/config.js` + `VITE_API_URL`
- Deploy Vercel project **lily-ai**; user tự tắt Deployment Protection

### Đợt 2 — Thêm domain Kinh tế chính trị (MLN122)
- `data/GiaoTrinh_KinhTeChinhTri_MacLenin.pdf` (262 trang, copy từ root, có text layer)
- `ChuDe4Presentation.pdf` (31 trang "Cạnh tranh và Độc quyền") → `data/Slide_KTCT_OCR.md` (`## [Slide KTCT N]`) + 31 ảnh `frontend/public/slides_ktct/` (render 1.5x q70, ~12MB)
- `ingest.py` generalize slide branch (mọi file `Slide*_OCR.md`, label tự do)
- Prompts thêm domain KTCT + rule trích `[Slide KTCT N]`; FAISS persona tương tự
- ChatPage viewer 2 deck (regex riêng cho `[Slide KTCT N]`, ảnh theo deck, cả mobile + desktop + thumbnail)
- Re-ingest cả 2 pipeline (nhớ XÓA `chroma_db/` trước — xem mục 6)

### Đợt 3 — Website 2 môn học
- Parse `BoCauHoi_ChuDe4.txt` → `frontend/src/data/quiz_ktct.json` (60 câu × 3 đáp án, đã assert)
- `frontend/src/data/subjects.js`: metadata 2 môn (lessons, quiz, quizGroups, slideDir, slideCount)
- Routes mới: `/quiz/:subject?`, `/lesson/:subject/:id` (legacy `/quiz`, `/lesson/:id` vẫn chạy, mặc định mln111)
- QuizPage: tab chuyển môn ở sidebar, reset điểm khi đổi môn; LessonPage: theo môn; LandingPage: redesign 2 card môn, stats tự tính; ChatPage: thêm quick-prompt KTCT
- Bài học KTCT: 4 bài (slides 3-8, 9-15, 16-21, 22-30); nhóm quiz: 1-22, 23-35, 36-49, 50-53, 54-60

### Domain
- **https://lily-hiro.vercel.app** — domain duy nhất (user yêu cầu). `lily-ai-ten.vercel.app` đã xóa qua API. **`lily-ai.vercel.app` là site của NGƯỜI KHÁC** — đừng nhầm.

## 4. Trạng thái đang chạy (lúc kết thúc session)

- Backend Lily: chạy nền local port 8000 (`main.py api`)
- Tunnel: **đã chuyển sang ngrok static domain** (18/07) — URL cố định trong `NGROK_DOMAIN` của `.env`, không cần redeploy Vercel khi restart. Khởi động cả hệ: `.\start_all.ps1`; tắt: `.\stop_all.ps1`. (Bản build Vercel hiện tại vẫn bake URL cloudflare cũ — cần redeploy 1 lần cuối sau khi user setup ngrok, xem GUIDE mục setup.)
- Robot bridge: mcp_pipe.py chạy nền, đã kết nối wss://api.xiaozhi.me OK (token thật trong `.env`, hạn tới ~2027). Khởi động lại: xem GUIDE_KHOI_DONG.md Bước 6
- Vercel: production alias lily-hiro.vercel.app, protection OFF
- Render DAC: service `DongAnhCapital` (srv-d5rqvl63jp1c73dmttn0, Singapore, free tier — ngủ sau 15p, cold start ~60s)
- **Lịch sử Git là nguồn sự thật** cho trạng thái thay đổi và các mốc đã commit. Kiểm tra `git status` và `git log` trước khi tiếp tục; không suy luận trạng thái từ handoff này.

## 5. Chưa làm / chờ user

1. **Setup ngrok (user, 1 lần, ~10 phút)**: tạo tài khoản + claim static domain + authtoken + `NGROK_DOMAIN` vào `.env` (từng bước trong GUIDE_KHOI_DONG.md mục setup). Sau đó **redeploy Vercel 1 lần cuối** với URL ngrok (lệnh trong GUIDE) — từ đó không phải redeploy vì tunnel nữa.
2. Test robot bằng giọng nói thật (câu triết học + câu KTCT + "VNINDEX hôm nay" + câu dẫn tới Hiro) — persona giọng nói mới cần nghe thật để chỉnh
3. Chạy thử toàn bộ kịch bản với robot thật trước ngày thuyết trình (checklist trong PRESENTATION.md)
4. Chưa verify giao diện 2 môn + streaming bằng mắt trên browser — mới verify bằng curl/bundle content
5. Quay video/screenshot dự phòng (Hiro + robot) như PRESENTATION.md liệt kê

## 6. BẪY & LƯU Ý (quan trọng nhất file này)

**Môi trường máy:**
- `python` bare = 3.14; **luôn dùng `py -3.11`** hoặc `venv\Scripts\python.exe`. Venv phải tên `venv/` (mcp_config.json expect `../venv/Scripts/python.exe`)
- PowerShell 5.1: không có `&&`, escape `"` trong lệnh dễ vỡ — chuỗi phức tạp thì dùng Git Bash
- Console cp1252: in tiếng Việt từ Python sẽ crash — set `PYTHONIOENCODING=utf-8`
- RAM 8GB — đừng chạy build + ingest + backend cùng lúc

**Mạng:**
- Tunnel chính giờ là **ngrok** (TCP/TLS 443 — không bị ảnh hưởng bởi chặn QUIC/UDP). cloudflared chỉ còn là dự phòng khẩn cấp: BẮT BUỘC `--protocol http2`, cần ~15-30s propagate (lỗi 1033 lúc đầu là bình thường), repoint web bằng `localStorage.LILY_API_URL` không cần redeploy
- **Port 8000 conflict (bẫy mới 18/07)**: dev server DongAnhCapital local (`uvicorn main:app --host 127.0.0.1 --port 8000`) bind 127.0.0.1 sẽ **cướp mọi request localhost** của Lily (bind 0.0.0.0) — web/tunnel/robot đều hỏng khó hiểu. `start_all.ps1` tự phát hiện và chặn; đừng chạy 2 server cùng lúc
- GitHub clone rất chậm (~600KB/s) — shallow clone + background + timeout 10 phút

**Code/pipeline:**
- **`Chroma.from_documents` APPEND chứ không overwrite** → luôn `Remove-Item -Recurse chroma_db` trước khi re-ingest, và phải TẮT backend trước (giữ lock sqlite)
- FAISS ingest thì ghi đè `mcp/.rag_index/index.pkl` an toàn, không cần xóa
- requirements.txt của repo THIẾU `langchain-groq`; bản groq/langchain-groq phải upgrade đồng bộ (lỗi `deepcopy_minimal`) — venv hiện tại đã đúng (groq 0.37.1 + langchain-groq 1.1.3)
- Đã fix bug có sẵn: `rag_pipeline_faiss.py` `relative_to(ROOT)` → `relative_to(ROOT.parent)`
- Citation KTCT cố tình dạng `[Slide KTCT N]` để KHÔNG match regex deck cũ `\[Slide\s*(\d+)\]` — đổi format là vỡ viewer
- Read tool đọc PDF >100MB sẽ fail và metadata số trang có thể sai (báo 4273, thực tế 31) — dùng pymupdf trong venv để thao tác PDF

**Vercel:**
- Team này bật Deployment Protection mặc định cho project mới — tạo project mới nhớ tắt (user tự tắt trên dashboard; **classifier chặn Claude tự sửa qua API** — đừng thử lại, hãy nhờ user)
- `vercel domains rm` KHÔNG xóa được subdomain cấp project → dùng REST API: `DELETE /v9/projects/lily-ai/domains/<domain>?teamId=team_VbCMm63EOZWCK4yuFqal9Qev` với token tại `%APPDATA%\xdg.data\com.vercel.cli\auth.json`
- Deploy chuẩn (login: findahuman): build local + prebuilt. **CẢNH BÁO: `vercel deploy --build-env VITE_API_URL=...` KHÔNG bake env vào bundle (đã dính 17/07 — bundle fallback localhost:8000). Luôn build local rồi kiểm tra bundle trước khi đẩy.**

**Nội dung:**
- Không bao giờ cam kết/hứa lợi nhuận trong bất kỳ nội dung nào liên quan DAC (rule cứng của DAC); confidence = độ tin cậy model, không phải tỷ lệ thắng
- Robot đọc to câu trả lời → output tool/prompt phía MCP phải NGẮN

## 7. Bản đồ file quan trọng

| File | Vai trò |
|---|---|
| `.env` | GROQ + Gemini key (thật) + MCP_ENDPOINT (placeholder!) — gitignored |
| `data/DongAnhCapital_KnowledgeBase.md` | Tri thức DAC + Hiro cho Lily |
| `data/Slide_KTCT_OCR.md` + `data/GiaoTrinh_KinhTeChinhTri_MacLenin.pdf` | Tri thức KTCT |
| `app/rag/prompts.py` | Persona Lily + rule trích dẫn 4 nguồn |
| `app/rag/llm_provider.py` | Groq primary + Gemini fallback dùng chung cho web/robot/FAISS |
| `app/rag/ingest.py` | Split slide generalize (`Slide*_OCR.md`) |
| `mcp/mcp_rag.py` | MCP server robot + 3 tool live DAC (cache) + backend-first `rag_answer` |
| `mcp/rag_pipeline_faiss.py` | FAISS pipeline dự phòng + persona giọng nói |
| `start_all.ps1` / `stop_all.ps1` / `keepalive_dac.ps1` | Khởi động/tắt 1 lệnh + giữ Render DAC thức |
| `frontend/src/data/subjects.js` | Nguồn duy nhất: 2 môn, lessons, quiz |
| `frontend/src/data/quiz_ktct.json` | 60 câu KTCT (generated — sửa thì sửa BoCauHoi rồi parse lại) |
| `frontend/src/config.js` | API_BASE (localStorage override → VITE_API_URL) + `apiFetch` (header ngrok) |
| `frontend/public/slides_ktct/` | 31 ảnh slide KTCT (generated từ ChuDe4Presentation.pdf) |
| `PRESENTATION.md` | Kịch bản 3 phần + checklist ngày D + dự phòng |
| `todolist.txt` | Việc xong / chờ / lệnh nhanh |

Memory dài hạn của Claude: `C:\Users\namet\.claude\projects\D--VsCode-LilyAndHiro\memory\lily-hiro-project-setup.md`

## 8. Lệnh nhanh (từ root repo)

```powershell
# TẤT CẢ trong 1 lệnh (backend + ngrok + robot + DAC warm-up + keep-alive)
.\start_all.ps1
# Tắt tất cả
.\stop_all.ps1

# Thủ công từng phần (dự phòng — chi tiết trong GUIDE_KHOI_DONG.md):
venv\Scripts\python main.py api                                  # backend
.\ngrok.exe http --domain=<NGROK_DOMAIN> 8000                    # tunnel cố định
cd mcp; ..\venv\Scripts\python mcp_pipe.py                       # robot

# Redeploy frontend (CHỈ khi đổi domain ngrok / sửa code FE; --build-env KHÔNG hoạt động)
cd frontend
vercel pull --yes --environment production
$env:VITE_API_URL='https://<NGROK_DOMAIN>'; vercel build --prod --yes
vercel deploy --prebuilt --prod --yes

# Re-ingest (TẮT backend + XÓA chroma_db trước)
venv\Scripts\python main.py ingest
cd mcp; ..\venv\Scripts\python rag_pipeline_faiss.py ingest

# Test nhanh
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"message":"..."}'
curl -X POST http://localhost:8000/chat/robot -H "Content-Type: application/json" -d '{"message":"..."}'
curl -N -X POST http://localhost:8000/chat/stream -H "Content-Type: application/json" -d '{"message":"..."}'
cd mcp; ..\venv\Scripts\python rag_pipeline_faiss.py ask "..."
```
