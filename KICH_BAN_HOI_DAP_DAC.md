# Kịch bản hỏi đáp với Lily — Giới thiệu Đông Anh Capital

> Robot XiaoZhi (Lily) trả lời từng câu ngắn 2–3 câu nói. Người thuyết trình (MC) hỏi **lần lượt từng câu**, chờ Lily nói xong hẳn rồi mới hỏi câu tiếp theo.
> Tổng: **15 câu, 5 hồi, ~10–12 phút** (tính cả lời dẫn). Bản tóm tắt toàn buổi: `PRESENTATION.md`.

## Nguyên tắc khi hỏi robot (đọc kỹ trước buổi)

1. **Đọc câu hỏi đúng nguyên văn** in đậm bên dưới — mỗi câu đã được thiết kế chứa tên nói "Đông Anh Capital" để ASR ghi nhận đúng và hệ thống định tuyến vào tài liệu DongAnh Capital. Đổi cách hỏi tùy hứng có thể làm Lily trả lời lệch.
2. **Nói chậm, rõ, gọn** — micro robot bắt câu ngắn tốt hơn câu dài có nhiều vế.
3. **Chờ Lily nói xong hẳn** (im lặng ~2 giây) rồi mới hỏi tiếp; hỏi chen ngang sẽ cắt câu trả lời.
4. Nếu Lily trả lời lệch hoặc nghe nhầm: bình tĩnh nói *"Mình hỏi lại nhé"* rồi đọc lại nguyên văn câu hỏi — khán giả coi đó là chuyện bình thường của demo giọng nói.
5. Ba câu ở Hồi 4 là **dữ liệu thật qua API** — đã có cơ chế cache: nếu máy chủ Đông Anh Capital đang ngủ, Lily tự nói "số liệu phiên gần nhất mình có là..." — vẫn là điểm cộng, cứ để Lily nói.
6. **Phát âm thương hiệu:** MC và Lily đều nói **"Đông Anh Capital"** — "Đông Anh" bằng tiếng Việt, "Capital" bằng tiếng Anh. Khi đọc website, nói **"Đông Anh Capital chấm com"**, không đánh vần chuỗi `donganhcapital.com`.

---

## HỒI 1 — Mở màn: Đông Anh Capital là gì? (2 câu, ~1,5 phút)

### Câu 1

**Lời dẫn (MC):** "Học kỳ trước Lily chỉ biết triết học. Bây giờ kho tri thức của Lily đã được bổ sung tài liệu về một dự án đang chạy thật trên Internet. Để Lily tự giới thiệu nhé."

**Hỏi robot:**
> **"Lily ơi, giới thiệu về Đông Anh Capital đi."**

**Đáp án kỳ vọng (Lily):** Đông Anh Capital là nền tảng phân tích chứng khoán Việt Nam dùng trí tuệ nhân tạo, cung cấp tín hiệu giao dịch máy học hằng ngày, dữ liệu VNINDEX thời gian thực, tin tức, báo cáo và trợ lý AI tư vấn đầu tư tên là Hiro — theo tài liệu Đông Anh Capital.

**Nguồn:** KB tĩnh (`data/DongAnhCapital_KnowledgeBase.md`, mục "donganhcapital.com là gì").
**Dự phòng:** nếu Lily im lặng/lỗi → hỏi lại y nguyên; nếu vẫn lỗi → MC tự giới thiệu 1 câu rồi nhảy sang Câu 2.

### Câu 2

**Lời dẫn:** "Nghe 'Capital' nhiều người sẽ tưởng đây là quỹ đầu tư. Hỏi Lily cho rõ."

**Hỏi robot:**
> **"Đông Anh Capital có phải là quỹ đầu tư không?"**

**Đáp án kỳ vọng:** Không — không quản lý tiền, không giao dịch thay ai; chỉ cung cấp dữ liệu, phân tích và tín hiệu tham khảo, quyết định cuối thuộc về nhà đầu tư. Sứ mệnh: đưa công cụ phân tích cấp tổ chức đến nhà đầu tư cá nhân.

**Nguồn:** KB tĩnh (mục mới "Có phải quỹ đầu tư không").
**Ý nghĩa cho MC chốt lại:** đây là câu định vị pháp lý + đạo đức quan trọng nhất — nhấn lại một câu: *"Nền tảng phân tích, không phải quỹ."*

---

## HỒI 2 — Tham quan website (3 câu, ~2 phút)

> Trong hồi này nên **chiếu song song tab tương ứng** trên donganhcapital.com khi Lily nói.

### Câu 3

**Lời dẫn:** "Vậy trên website có những gì? Nhờ Lily dẫn tour."

**Hỏi robot:**
> **"Website Đông Anh Capital có những tab chính nào?"**

**Đáp án kỳ vọng:** Khoảng mười tab — nổi bật là Dashboard, AI Analyst, Pro Signals, BCD Signals, News, Reports và AI Chat nơi trò chuyện với Hiro.

**Nguồn:** KB tĩnh (mục "Các tab chính").
**Thao tác màn hình:** rê chuột qua thanh menu của donganhcapital.com theo lời Lily.

### Câu 4

**Lời dẫn:** "Bắt đầu từ tab đầu tiên mà ai vào cũng thấy — Dashboard." *(mở tab Dashboard)*

**Hỏi robot:**
> **"Tab Dashboard của Đông Anh Capital cho xem gì?"**

**Đáp án kỳ vọng:** Bản đồ nhiệt 226 mã cổ phiếu trên ba sàn HOSE, HNX, UPCoM — ô xanh tăng, ô đỏ giảm, nhìn một cái thấy sức khỏe cả thị trường; kèm VNINDEX và phái sinh VN30F1M trong phiên.

**Nguồn:** KB tĩnh (mục Dashboard + dữ liệu thị trường).
**Thao tác màn hình:** đúng lúc Lily nói "ô xanh ô đỏ", chỉ vào heatmap đang chiếu — khớp hình với lời là khoảnh khắc "wow" đầu tiên.

### Câu 5

**Lời dẫn:** "Ngoài số liệu, nhà đầu tư còn cần tin tức. Tab News có gì hay?" *(mở tab News)*

**Hỏi robot:**
> **"Tin tức trên Đông Anh Capital có gì đặc biệt?"**

**Đáp án kỳ vọng:** Gom tin CafeF Việt Nam + tin vĩ mô thế giới; AI tự gắn nhãn cảm xúc từng tin — Tích cực, Tiêu cực, Trung lập — lướt qua là biết tin nào đáng chú ý.

**Nguồn:** KB tĩnh (mục Tin tức).
**Thao tác màn hình:** chỉ vào các badge màu Tích cực/Tiêu cực trên trang News.

---

## HỒI 3 — Bộ não AI: ba mô hình (4 câu, ~3 phút)

### Câu 6

**Lời dẫn:** "Trái tim của nền tảng là các mô hình máy học. Hỏi Lily bức tranh tổng thể trước."

**Hỏi robot:**
> **"Tín hiệu AI của Đông Anh Capital hoạt động thế nào?"**

**Đáp án kỳ vọng:** Ba mô hình độc lập — Breakout, LTR, BCD — tự chạy sau mỗi phiên lúc 15 giờ 02, quét toàn thị trường, ra tín hiệu kèm điểm tin cậy; điểm tin cậy là độ tin cậy của mô hình, **không phải tỷ lệ thắng**.

**Nguồn:** KB tĩnh (mục "Tín hiệu AI hoạt động thế nào").
**Lưu ý:** nếu Lily quên vế "không phải tỷ lệ thắng", MC tự bổ sung — vế này bắt buộc phải vang lên trong hội trường.

### Câu 7

**Hỏi robot:**
> **"Mô hình Breakout của Đông Anh Capital làm gì?"**

**Đáp án kỳ vọng:** Quét 226 mã sau mỗi phiên tìm cổ phiếu sắp đột phá giá; tín hiệu kèm giá vào lệnh, chốt lời, cắt lỗ, điểm tin cậy. Rất chọn lọc — có ngày không phát tín hiệu nào.

**Nguồn:** KB tĩnh. **Màn hình:** tab AI Analyst.

### Câu 8

**Hỏi robot:**
> **"Mô hình LTR của Đông Anh Capital là gì?"**

**Đáp án kỳ vọng:** Learning to Rank — học xếp hạng: chấm điểm và xếp hạng toàn bộ cổ phiếu theo tiềm năng tăng giá tương đối, mỗi ngày chọn tốp 5 mã triển vọng nhất ở tab Pro Signals.

**Nguồn:** KB tĩnh. **Màn hình:** tab Pro Signals.

### Câu 9

**Hỏi robot:**
> **"Mô hình BCD của Đông Anh Capital là gì?"**

**Đáp án kỳ vọng:** Mô hình bắt đáy: nhận diện mẫu hình đáy B — đáy C thấp hơn — thủng đáy C, rồi ước tính xác suất phục hồi ít nhất 15% trong 60 phiên tiếp theo.

**Nguồn:** KB tĩnh. **Màn hình:** tab BCD Signals.
**Chuyển mạch sang Hồi 4 (MC):** "Ba mô hình này không nằm trên giấy — chúng đang chạy thật. Và Lily có thể lấy số liệu thật, ngay bây giờ."

---

## HỒI 4 — ⭐ Demo LIVE: Lily gọi API thật (3 câu, ~2,5 phút)

> Ba câu này Lily **không đọc tài liệu** mà gọi tool MCP → API `donganhcapital.onrender.com`. Đây là cao trào của phần robot. Số liệu là thật của phiên gần nhất — MC không cần biết trước đáp án, cứ để khán giả nghe cùng.

### Câu 10

**Lời dẫn:** "Câu này không có trong tài liệu nào cả — Lily phải tự đi lấy số liệu."

**Hỏi robot:**
> **"VNINDEX hôm nay thế nào?"**

**Đáp án kỳ vọng (dạng):** "VNINDEX phiên [ngày]: đóng cửa [X] điểm, tăng/giảm [Y] điểm ([Z]%) so với phiên trước. Khối lượng [N] triệu đơn vị."

**Nguồn:** tool live `dac_vnindex` (API `/vnindex`).
**Dự phòng:** máy chủ ngủ → Lily tự nói "số liệu phiên gần nhất mình có là..." (cache) — vẫn hợp lệ. Nếu hoàn toàn không có số → Lily mời xem trực tiếp Đông Anh Capital chấm com; MC mở Dashboard chỉ số thật.

### Câu 11

**Hỏi robot:**
> **"Hôm nay AI của Đông Anh Capital có tín hiệu gì?"**

**Đáp án kỳ vọng (dạng):** "Tín hiệu AI breakout gần nhất: ngày [D], [N] mã. Mã [ABC]: giá vào [x] nghìn đồng, mục tiêu [y], cắt lỗ [z]... Lưu ý tín hiệu chỉ mang tính tham khảo, muốn phân tích sâu hơn hãy hỏi Hiro."
Nếu gần đây không có tín hiệu: "Mô hình rất chọn lọc, chỉ báo khi xác suất đủ tốt" — **cũng là câu trả lời đẹp**, minh họa tính kỷ luật của mô hình.

**Nguồn:** tool live `dac_ai_signals_today` (API `/ai-signals`).
**Màn hình:** mở tab AI Analyst đối chiếu đúng các mã Lily vừa đọc.

### Câu 12

**Hỏi robot:**
> **"Mã nào tăng giảm mạnh nhất hôm nay?"**

**Đáp án kỳ vọng (dạng):** "Top tăng: [A], [B], [C]. Top giảm: [D], [E], [F]. Dữ liệu từ Đông Anh Capital chấm com, chỉ mang tính tham khảo."

**Nguồn:** tool live `dac_market_movers` (API `/market-status`, đã lọc mã thanh khoản thấp).
**Chốt hồi (MC):** "Các bạn vừa nghe một con robot đọc số liệu thật của thị trường chứng khoán Việt Nam, lấy trực tiếp từ API của Đông Anh Capital chấm com — không phải kịch bản thu sẵn."

---

## HỒI 5 — Giá, minh bạch, và cú chốt Hiro (3 câu, ~2 phút)

### Câu 13

**Lời dẫn:** "Chắc nhiều bạn đang hỏi: dùng thì tốn bao nhiêu?"

**Hỏi robot:**
> **"Dùng Đông Anh Capital có mất phí không?"**

**Đáp án kỳ vọng:** Gói Free miễn phí trọn đời, không cần thẻ. Pro 199 nghìn/tháng mở tín hiệu nâng cao và Hiro, có dùng thử miễn phí 1 tuần; Premium 499 nghìn/tháng thêm báo cáo PDF và Hiro không giới hạn.

**Nguồn:** KB tĩnh (mục Gói dịch vụ). **Màn hình:** khu pricing trên trang chủ.

### Câu 14

**Lời dẫn:** "Câu hỏi mà mọi nền tảng tài chính đều phải trả lời thẳng."

**Hỏi robot:**
> **"Đông Anh Capital có cam kết lợi nhuận không?"**

**Đáp án kỳ vọng:** Không. Mọi tín hiệu chỉ mang tính tham khảo, không phải lời khuyên đầu tư; đầu tư luôn có rủi ro, nhà đầu tư tự chịu trách nhiệm.

**Nguồn:** KB tĩnh (mục Miễn trừ trách nhiệm).
**Ý nghĩa:** để chính AI nói câu từ chối cam kết — minh chứng sống cho triết lý "AI trung thực về giới hạn của mình". MC nhấn lại đúng 1 câu này.

### Câu 15 — cú chốt

**Lời dẫn:** "Câu cuối cùng cho Lily."

**Hỏi robot:**
> **"Muốn được tư vấn sâu về một mã cổ phiếu thì hỏi ai?"**

**Đáp án kỳ vọng:** Hãy hỏi Hiro — AI cố vấn đầu tư tại tab AI Chat trên Đông Anh Capital chấm com; Hiro tra giá, tín hiệu, tin tức thật để tư vấn từng mã cụ thể; cần gói Pro trở lên.

**Nguồn:** KB tĩnh (mục Hiro).
**Kịch bản chốt (MC):** *(mở tab AI Chat, gõ cho Hiro: "Nhận định về FPT hôm nay?")* — "Lily vừa giới thiệu các bạn với đồng nghiệp của mình. Một hệ sinh thái hai AI: Lily rèn tư duy, Hiro thực chiến thị trường. Cùng một triết lý: trả lời bằng dữ liệu thật và trung thực về giới hạn của mình."

---

## Câu hỏi dự phòng (phần giao lưu với khán giả)

Kho tri thức của Lily đã phủ sẵn các câu sau — nếu khán giả hỏi, cứ đưa micro cho robot:

| Câu hỏi | Ý trả lời có trong KB |
|---|---|
| "Ai xây dựng Đông Anh Capital?" / "Trụ sở ở đâu?" | Đội 6 kỹ sư + chuyên viên phân tích; Khu CNC Hòa Lạc, Hà Nội |
| "AI Agent của Đông Anh Capital là gì?" | Sắp ra mắt quý 4/2026: đọc tin, học phong cách, gợi ý lệnh, chỉ thực hiện khi được duyệt — **luôn nói "đang phát triển"** |
| "Hiro khác gì Lily?" | Lily: triết học, rèn tư duy; Hiro: cố vấn chứng khoán, dữ liệu thật |
| "Điểm tin cậy 87% có phải tỷ lệ thắng không?" | Không — là độ tự tin của mô hình; hiệu suất công khai ở tab Data Analyst |
| "Đông Anh Capital dùng công nghệ gì?" | React + FastAPI + PostgreSQL/MongoDB; model LightGBM, XGBoost; Hiro chạy Gemini có grounding |
| "Mua gói bằng cách nào?" | Chuyển khoản VietQR (SePay), xác nhận tự động vài giây |

## Điều Lily (và MC) KHÔNG được nói

1. **Không** gọi con số ~87% là "tỷ lệ thắng" hay "độ chính xác" — đó là **điểm tin cậy của mô hình**. (Đã khắc trong KB + system prompt.)
2. **Không** nêu con số lợi nhuận cụ thể ("+23%", "lãi X%/tháng") — các con số trên landing page là minh họa marketing.
3. **Không** giới thiệu các "khách hàng" trong mục testimonial (Nguyễn Minh Tuấn, Trần Thị Lan...) như người thật — đó là nội dung minh họa.
4. **Không** nói AI Agent "đã có" — luôn là "sắp ra mắt, quý 4 năm 2026".
5. **Không** để Lily/MC khuyến nghị mua bán một mã cụ thể — mọi câu tư vấn sâu đều chuyển cho Hiro kèm disclaimer.

## Checklist trước giờ G (bổ sung cho checklist trong PRESENTATION.md)

1. [ ] Chạy `.\start_all.ps1` → chờ khối **READY** (backend + ngrok + robot + đánh thức DAC).
2. [ ] **Prime cache số liệu live**: hỏi robot lần lượt cả 3 câu Hồi 4 ("VNINDEX hôm nay thế nào?", "Hôm nay AI của Đông Anh Capital có tín hiệu gì?", "Mã nào tăng giảm mạnh nhất hôm nay?") — vừa test vừa ghi cache `.dac_cache.json` phòng Render ngủ giữa buổi.
3. [ ] Test nhanh 3 câu KB đại diện: Câu 2 (quỹ đầu tư), Câu 8 (LTR), Câu 15 (Hiro).
4. [ ] Mở sẵn các tab donganhcapital.com theo thứ tự hồi: Trang chủ → Dashboard → News → AI Analyst → Pro Signals → BCD Signals → pricing → AI Chat (đăng nhập sẵn tài khoản Pro/Premium).
5. [ ] **KHÔNG chạy dev server DongAnhCapital local** (chiếm port 8000, cướp request của Lily).
6. [ ] Nếu vừa sửa `data/DongAnhCapital_KnowledgeBase.md`: đã re-ingest cả ChromaDB lẫn FAISS chưa? (Xem `HANDOFF.md` mục ingest — nhớ xóa `chroma_db/` trước.)

## Xử lý sự cố nhanh giữa buổi

| Sự cố | Xử lý |
|---|---|
| Robot không nghe/không đáp | Hỏi lại nguyên văn; lần 2 vẫn hỏng → chuyển câu đó sang web chat https://lily-hiro.vercel.app (cùng bộ não) |
| Backend Lily chết | Robot tự fallback FAISS local — cứ demo tiếp, chất lượng chỉ giảm nhẹ |
| Render (API DAC) ngủ | Lily tự đọc số cache "phiên gần nhất" — hợp lệ; hoặc mở donganhcapital.com chỉ số trực tiếp |
| Lily trả lời sai dữ kiện | MC đính chính ngắn gọn rồi đi tiếp — không dừng lại debug trước khán giả |
| Mất mạng toàn bộ | Robot vẫn trả lời câu KB bằng FAISS local; phần web dùng screenshot/video dự phòng |
