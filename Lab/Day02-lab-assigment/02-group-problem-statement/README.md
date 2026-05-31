# 02 — Group Problem Statement (bản nộp nhóm)

> Nhóm 4 người: **Khoa** (mình), **An**, **Bình**, **Chi**. Mỗi người mang top 3 candidate problems vào → 12 candidates. Tài liệu này là bản cuối nhóm thống nhất; mỗi thành viên copy bản này vào repo cá nhân của mình.
>
> ⚠️ Số liệu validation (interview/poll) dưới đây là **kết quả kiểm chứng nhanh của nhóm trong lab + một phần giả định cần xác nhận thêm**. Phần nào là giả định đều được ghi rõ. Không dùng số liệu vendor để làm metric.

---

## Phase 3 — Group Convergence (từ 12 candidates về 1)

### Bước 3.1 — Trình bày top 3

| #  | Người đưa ra | Candidate problem                                   | Người gặp vấn đề        | Điểm nghẽn                          | Cảm nhận nhanh |
|----|--------------|-----------------------------------------------------|-------------------------|-------------------------------------|----------------|
| 1  | Khoa         | Câu hỏi quy trình lặp lại trong Discord CLB          | Member mới + người phụ trách | Chờ trả lời + trả lời lặp           | Workflow rõ, đo được |
| 2  | Khoa         | Tổng hợp ghi chú ôn thi từ nhiều nguồn               | SV ôn thi               | Viết bộ tổng hợp                    | Metric khó |
| 3  | Khoa         | Tìm lại quyết định cũ trong Discord                  | Nhóm dự án              | Đọc nhiều thread cũ                 | Trùng #1 |
| 4  | An           | Ban tổ chức trả lời cùng câu hỏi event qua DM        | Ban tổ chức + người tham gia | Trả lời lặp trước mỗi event         | Trùng cụm với #1 |
| 5  | An           | Phân loại email/thông báo từ trường                  | SV                      | Lọc thông báo lẫn lộn               | Có thể là Rule |
| 6  | An           | Onboard member mới vào codebase CLB                  | Member mới + maintainer | Tự dò code chạy thế nào             | Scope rộng |
| 7  | Bình         | Action item sau họp không rõ ai làm gì               | Thành viên nhóm         | Ghi + giao việc                     | Pain thật, hơi mơ hồ |
| 8  | Bình         | Tổng hợp feedback Google Form sau workshop           | Ban nội dung            | Đọc + tổng hợp form                 | Lặp lại, đo được |
| 9  | Bình         | Đọc paper viết related work                           | SV research             | Đọc + tóm tắt paper dài             | Quality khó đo |
| 10 | Chi          | Viết standup/update mỗi sáng                          | Cá nhân                 | Gõ lại cùng format                  | Scope nhỏ |
| 11 | Chi          | Tìm người phụ trách đúng việc trong CLB              | Member mới              | Không biết hỏi ai                   | Trùng cụm với #1 |
| 12 | Chi          | Nhắc deadline cá nhân nhưng quên context             | Cá nhân                 | Theo dõi nhiều deadline             | Có thể là Rule |

### Bước 3.2 — Gom trùng / cluster

| Cluster | Candidates included | Pattern chung | Ghi chú |
|---------|---------------------|---------------|---------|
| A — Kiến thức kẹt trong chat → hỏi lại / khó tìm | 1, 3, 4, 11 | Thông tin đã tồn tại nhưng trôi mất; người ta hỏi lại hoặc đi tìm thủ công | Cụm lớn nhất, nhiều người đau |
| B — Tổng hợp nhiều nguồn thành 1 bản đọc được | 2, 8, 9 | Gom nguồn rời rạc rồi viết lại cho người khác | Giống cụm "report" trong ví dụ mẫu |
| C — Phân loại / nhắc việc | 5, 12 | Lọc & nhắc theo luật rõ | Phần lớn là Rule, ít cần AI |
| D — Giao việc / onboard | 6, 7, 10 | Thiếu cấu trúc handoff sau họp / khi vào mới | Pain thật nhưng mơ hồ, khó đo trong lab |

Nhận xét: cụm **A** xuất hiện ở 3/4 thành viên (Khoa, An, Chi) — tín hiệu cho thấy đây là pain chung và dễ hiểu domain.

### Bước 3.3 — Shortlist

| Candidate | Vì sao vào shortlist | Rủi ro / điều chưa rõ |
|-----------|----------------------|------------------------|
| A. Câu hỏi quy trình lặp lại trong Discord (gộp 1+4+11) | Cả nhóm vừa là người hỏi vừa là người trả lời; workflow rõ; metric thời gian đo được | "Trả lời đúng" đo thế nào; chất lượng KB ban đầu |
| B. Tổng hợp feedback Google Form sau workshop (#8) | Lặp lại, có baseline thời gian rõ | Ít người làm (chỉ ban nội dung); impact hẹp |
| D. Action item sau họp (#7) | Pain thật, nhiều người gặp | Khó đo; phụ thuộc thói quen ghi chép, không hẳn bài toán AI |

### Bước 3.4 — Score để đồng thuận

Chấm 1-5. Mục tiêu là ép nhóm nói rõ lý do, không phải điểm tuyệt đối.

| Candidate | Actor rõ | Workflow rõ | Pain có evidence | Impact đo được | Làm trong lab | So sánh R/W/A được | Nhóm hiểu domain | Tổng |
|-----------|---------:|------------:|-----------------:|---------------:|--------------:|-------------------:|-----------------:|-----:|
| A. Discord repeated Q | 5 | 5 | 4 | 4 | 5 | 5 | 5 | **33** |
| B. Form feedback      | 4 | 5 | 3 | 5 | 5 | 3 | 3 | 28 |
| D. Action item        | 4 | 3 | 4 | 2 | 3 | 3 | 4 | 23 |

**Candidate nhóm chọn: A — Câu hỏi quy trình lặp lại trong Discord CLB.**

Vì sao chọn:
- Cả 4 người đều trực tiếp trải nghiệm (vừa hỏi vừa trả lời) → hiểu domain sâu nhất.
- Workflow rõ và baseline thời gian đếm được ngay trong CLB.
- So sánh được sạch No AI / Rule / Workflow / Agent (đây là điểm B và D yếu hơn).

Vì sao không chọn các candidate còn lại:
- **B (Form feedback):** đo được nhưng chỉ ban nội dung gặp → impact hẹp, ít người hiểu domain.
- **D (Action item):** pain thật nhưng phụ thuộc thói quen ghi chép của người chủ trì họp; phần lớn là vấn đề quy trình, không chắc cần AI, và impact khó đo trong lab.

Nếu có disagreement: An ban đầu nghiêng về B vì "đo dễ nhất". Nhóm thống nhất rằng *đo dễ* không bằng *hiểu domain + so sánh được phương án*, nên chọn A và giữ B làm phương án dự phòng nếu A không validate được.

---

## Phase 4 — Quick Validation + Research

### Bước 4.1 — Quick validation

Nhóm dùng cả hai cách: phỏng vấn nhanh + poll nhỏ.

| Nguồn | Số người / mẫu | Tín hiệu xác nhận | Tín hiệu phản bác | Nhóm sửa problem thế nào |
|-------|---------------:|-------------------|-------------------|--------------------------|
| Quick interview (member + 1 trưởng ban) | 3 | 3/3 từng đăng câu hỏi quy trình rồi phải chờ; trưởng ban xác nhận hay phải trả lời lại cùng thứ | 1 người nói "phần lớn câu của mình là câu nhạy cảm (điểm), bot không nên trả lời" | Thêm boundary rõ: bot **chỉ** trả lời câu quy trình công khai, không trả lời câu nhạy cảm |
| Mini poll trong server CLB | 9 | 6/9 nói từng bỏ cuộc không tìm được câu trả lời cũ; 5/9 nói chờ trên 1 tiếng | 2/9 nói "pin bài là đủ rồi, không cần bot" | Giữ Rule (pinned/structure) làm nền; AI chỉ thêm phần hiểu câu hỏi diễn đạt tự nhiên |
| Đếm log #general (2 tuần) | ~14 câu hỏi quy trình | ~9/14 là câu đã từng được trả lời trước đó | — | Xác nhận baseline "câu lặp" là có thật, không chỉ cảm tính |

> ⚠️ Các con số trên là kiểm chứng nhanh trong phạm vi lab (mẫu nhỏ, một CLB). Đây là tín hiệu định hướng, **chưa phải bằng chứng đủ mạnh để chốt metric**. Cần đếm log dài hơn (4-6 tuần) trước khi cam kết con số cụ thể.

Insight sau validation:

```text
Pain thật không nằm ở "thiếu thông tin" — thông tin đã tồn tại đâu đó trong Discord.
Pain nằm ở (1) độ trễ vì thông tin trôi mất + người hỏi diễn đạt khác từ khóa nên
search trượt, và (2) gánh nặng trả lời lặp dồn lên vài người phụ trách.
=> Bài toán nên thu hẹp về: "trả lời nhanh & đúng các câu hỏi quy trình CÔNG KHAI,
   lặp lại", không phải "search toàn bộ lịch sử chat" hay "trả lời mọi câu".
```

### Bước 4.2 — Research giải pháp đã có

Nhóm tìm các hướng đã tồn tại để tránh nghĩ trong chân không. (Các claim hiệu quả của vendor được ghi là *vendor-claimed*; nhóm **không** dùng làm metric vì chưa verify được.)

| Nguồn / tool / case | Link | Họ giải quyết phần nào? | Điểm mạnh | Khoảng trống / rủi ro | Bài học cho nhóm |
|---------------------|------|--------------------------|-----------|------------------------|-------------------|
| Wallu — AI Discord support bot | https://wallubot.com/ | Trả lời FAQ từ docs/website/lịch sử kênh; định tuyến sang ticket | Chạy sẵn, nhiều ngôn ngữ, gắn được nhiều nguồn | Con số "giảm ~70-80% câu lặp" là *vendor-claimed*, chưa verify; phụ thuộc chất lượng nguồn nạp vào | Pattern hợp lý có sẵn: hỏi tự nhiên → trả lời từ KB. Không cần tự build từ đầu để pilot |
| Mava — AI knowledge base cho community | https://www.mava.app/blog/discord-faq-ai-knowledge-base | Gom pinned posts + docs + chat logs thành KB, trả lời trong Discord | Nhấn mạnh việc gom nguồn rời rạc về một chỗ rồi mới trả lời | Chất lượng phụ thuộc việc curate; KB rác → trả lời rác | Củng cố giả thuyết: bước **curate KB** quan trọng hơn bước trả lời |
| BetaHub — KB bot có "gap detection" | https://betahub.io/resources/knowledge-base-automate-discord-support/ | Trả lời từ KB + đánh dấu rõ đây là câu tự động + ghi lại câu bot không tự tin | Có cơ chế *minh bạch* (gắn nhãn auto) và *gap detection* (câu bot không trả lời được) | Vẫn cần người cập nhật nguồn; phụ thuộc tài liệu đúng | Lấy 2 ý cho thiết kế của nhóm: **gắn nhãn câu tự động** + **log câu bot không chắc** để con người bổ sung |
| IBM — RAG là gì | https://www.ibm.com/think/topics/retrieval-augmented-generation | Giải thích RAG neo câu trả lời vào nguồn dữ liệu thật | Nguồn uy tín; nói rõ RAG giảm hallucination nhưng **không** loại bỏ hoàn toàn | Là khái niệm, không phải tool | Bài học: RAG giúp giảm bịa, nhưng vẫn cần người review → cần human boundary |
| Azure AI Search — RAG overview | https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview | Mô tả vấn đề "similarity ≠ relevance" (hỏi một kiểu, tài liệu viết kiểu khác) | Chỉ ra đúng nguyên nhân search Discord hay trượt | Nội dung kỹ thuật, cần đọc chọn lọc | Đây chính là lý do search built-in trượt → RAG hiểu được diễn đạt khác nhau là giá trị thật của AI ở đây |

Research takeaway:

```text
1. Không cần build agent tự chạy. Pattern phổ biến và đủ là: KB curate + hỏi tự nhiên
   → RAG trả lời kèm nguồn → người thật cập nhật KB.
2. Giá trị AI thật sự ở đây là HIỂU câu hỏi diễn đạt khác từ khóa (similarity ≠ relevance),
   không phải "thông minh" hơn con người.
3. Hai cơ chế nên copy: gắn nhãn câu trả lời tự động (minh bạch) + log câu bot không chắc
   để con người bổ sung dần (gap detection).
4. RAG giảm chứ không xoá hallucination → bắt buộc có human boundary cho câu nhạy cảm.
```

---

## Phase 5 — Workflow + Problem Statement

### Bước 5.1 — Current workflow (bản nhóm)

| Bước | Actor | Input | Output | Thời gian/tần suất | Ghi chú |
|------|-------|-------|--------|--------------------|---------|
| 1 | Thành viên | Nhu cầu thông tin | Câu hỏi trong đầu | Mỗi lần cần | — |
| 2 | Thành viên | Từ khóa | Kết quả search Discord | ~5'/lần | Thường trượt vì diễn đạt khác từ khóa |
| 3 | Thành viên | Câu hỏi | Bài đăng #general | ~1' | Câu hỏi lặp dồn vào kênh chung |
| 4 | (chờ) | — | — | **median 1-3 tiếng** | **Bottleneck: độ trễ**, người hỏi đôi khi bỏ cuộc |
| 5 | Người phụ trách | Câu hỏi + trí nhớ | Câu trả lời | ~5-10'/câu, ~5-8 câu/tuần | **Bottleneck: trả lời lặp** |

Bottleneck chính:

```text
Bước 4-5: người hỏi chờ lâu (độ trễ) + người phụ trách trả lời lặp lại (gánh nặng).
Gốc rễ đẩy lên bottleneck: bước 2 search trượt vì similarity ≠ relevance.
```

### Bước 5.2 — Future workflow (bản nhóm)

```text
FUTURE STATE — câu thuộc KB: trả lời < 5 phút

[1 Thành viên hỏi bot bằng ngôn ngữ tự nhiên]
        │
        ▼
[2 Bot RAG tìm trong KB curate]  -- Workflow step (AI: hiểu diễn đạt + truy hồi)
        │
        ├── (a) độ tự tin CAO  → [3a Trả lời kèm link nguồn + nhãn "🤖 tự động"]  (< 1')
        │                              │
        │                              ▼
        │                        [4a Nếu sai → thành viên bấm "không đúng" → tag người thật]  -- Fallback
        │
        └── (b) độ tự tin THẤP hoặc câu NHẠY CẢM
                   → [3b Bot trả "mình chưa chắc" + tag người phụ trách]  -- Human boundary
                          │
                          ▼
                   [4b Người phụ trách trả lời câu mới/khó: ~5']  -- Human boundary
                          │
                          ▼
                   [5 Người phụ trách thêm cặp Q&A mới vào KB: ~2']  -- KB lớn dần, tự đỡ về sau

BOUNDARY:
- Bot chỉ trả lời câu QUY TRÌNH CÔNG KHAI.
- Bot KHÔNG trả lời điểm, đánh giá cá nhân, quyết định chưa công bố.
- Bot KHÔNG tự ra quyết định thay ban điều hành.

FALLBACK TỔNG:
- Nếu tỉ lệ "không đúng" cao trong 2 tuần → tắt auto-answer, quay về pinned FAQ (Rule) thủ công.
```

Before/after impact:

| Metric | Trước | Sau kỳ vọng | Ghi chú |
|--------|------:|------------:|---------|
| Median time-to-answer (câu trong KB) | 1-3 tiếng | **< 5 phút** | Target chính |
| % câu lặp được trả lời tự động & đúng | 0% | **≥ 70%** (top FAQ) | Phải đo cả "đúng", không chỉ "có trả lời" |
| Thời gian người phụ trách trả lời lặp/tuần | ~35' | **< 10'** | Chỉ còn xử lý câu mới/khó |
| Số bước người hỏi phải làm | 3 (search → đăng → chờ) | 1 (hỏi bot) | Giảm ma sát |
| Risk mới | Không có hallucination | Có hallucination + trả lời sai tự tin | Cần nhãn auto + nút báo sai + human review |

### Bước 5.3 — Problem Statement v0

| Field | Nội dung |
|-------|----------|
| **Actor** | Thành viên CLB (người hỏi) và người phụ trách ban kỹ thuật (người trả lời lặp). |
| **Workflow** | Thành viên cần thông tin → search Discord trượt → đăng #general → chờ 1-3 tiếng → người phụ trách tìm lại và trả lời → câu trả lời trôi xuống và lặp lại. |
| **Bottleneck** | Chờ trả lời (độ trễ) + người phụ trách trả lời lặp lại; gốc rễ là search trượt vì diễn đạt khác từ khóa. |
| **Impact** | ~5-8 câu lặp/tuần; người hỏi chờ 1-3 tiếng, đôi khi bỏ cuộc; người phụ trách mất ~35'/tuần; thông tin cũ/sai bị lan truyền. |
| **Success Metric** | Median time-to-answer 1-3h → dưới 5 phút; ≥70% câu lặp được trả lời tự động & đúng; thời gian trả lời lặp/tuần < 10'; không tăng câu trả lời sai. |
| **Boundary** | Chỉ trả lời câu quy trình công khai; không trả lời câu nhạy cảm; không chắc thì tag người thật; không tự quyết định thay ban điều hành. |

---

## Phase 6 — Rule / Workflow / Agent + Decision

### Bước 6.0 — Ma trận độ phù hợp

Tự kiểm nhanh:

| Câu hỏi | Trả lời của nhóm | Suy ra |
|---------|------------------|--------|
| Output có thể khác nhau mỗi lần mà vẫn chấp nhận được không? | Một phần — diễn đạt câu trả lời linh hoạt nhưng nội dung phải khớp nguồn | Độ mơ hồ **trung bình** |
| Cần phối hợp 3+ bước hoặc 3+ nguồn dữ liệu không? | Không nhiều — 1 KB curate + 1 bước truy hồi + 1 bước trả lời | Độ phức tạp **thấp-trung bình** |
| AI có cần tự quyết định bước tiếp theo không? | Không — luồng cố định: tìm → (trả lời / tag người) | **Không cần Agent** |

Bài toán nằm ở ô:

```text
Độ phức tạp thấp–trung bình × độ mơ hồ trung bình
→ "Workflow có AI hỗ trợ một bước" là phù hợp nhất.
```

Vì sao:

```text
Luồng cố định và ngắn. AI chỉ cần làm tốt MỘT việc (hiểu câu hỏi + truy hồi đúng từ KB
rồi diễn đạt lại kèm nguồn). Không có bước nào cần AI tự lập kế hoạch hay tự gọi nhiều
công cụ. Phần ra quyết định cuối vẫn ở người thật.
```

### Bước 6.1 — So sánh Rule / Workflow / Agent

| Mức | Phương án cho bài toán nhóm | Khi nào đủ | Rủi ro | Chọn? |
|-----|------------------------------|------------|--------|-------|
| **No AI / process** | Chuẩn hóa kênh + pinned FAQ + #announcements + quy ước hỏi đúng kênh | Đủ cho server nhỏ, ít câu hỏi | FAQ tĩnh lỗi thời; search vẫn trượt vì khác từ khóa | Dùng làm **nền**, không đủ một mình |
| **Rule** | Bot khớp từ khóa → trả câu trả lời cố định (kiểu `!faq <name>`) | Đủ nếu câu hỏi luôn dùng cùng từ khóa | Không hiểu diễn đạt tự nhiên; người vẫn phải nhớ đúng lệnh | Dùng cho vài câu cực phổ biến; không giải gốc |
| **Workflow** | RAG trên KB curate: hiểu câu hỏi tự nhiên → truy hồi → trả lời kèm nguồn; không chắc → tag người | Hợp vì luồng tuyến tính, AI hỗ trợ đúng 1 bước (hiểu + truy hồi) | Hallucination, trả lời sai tự tin → cần nhãn + nút báo sai + review | **Chọn** |
| **Agent** | Agent tự crawl toàn bộ lịch sử chat, tự quyết khi nào trả lời/khi nào hỏi thêm/khi nào escalate | Chỉ cần nếu phải tự lập kế hoạch nhiều bước, nhiều nguồn, nhiều tool | Quá rộng; rủi ro privacy (đọc cả chat riêng tư); khó kiểm soát; overkill | **Chưa chọn** |

Mức chọn:

```text
Workflow.
```

Vì sao chọn:
- AI chỉ hỗ trợ đúng một bước có giá trị thật: hiểu câu hỏi diễn đạt khác từ khóa + truy hồi đúng (similarity ≠ relevance) — chính là chỗ search built-in trượt.
- Luồng cố định, dễ đặt human boundary và fallback.
- Rủi ro kiểm soát được bằng nhãn "tự động" + nút báo sai + review KB.

Vì sao không chọn mức đơn giản hơn (Rule/No-AI):
- Pinned FAQ + Rule khớp từ khóa **không** giải được gốc rễ: người hỏi diễn đạt khác từ khóa nên vẫn trượt và vẫn đổ về #general. Đó là lý do AI (RAG) thêm giá trị thật.

Vì sao không chọn mức cao hơn (Agent):
- Không có bước nào cần AI tự lập kế hoạch hay tự quyết. Agent kéo theo rủi ro privacy (đọc toàn bộ chat) và chi phí kiểm soát lớn mà không thêm giá trị cho bài toán này.

### Bước 6.2 — Problem Statement v1

| Field | Nội dung |
|-------|----------|
| **Actor** | Thành viên CLB (người hỏi câu quy trình) + người phụ trách ban kỹ thuật (người trả lời lặp). |
| **Workflow** | Hỏi → (cũ: search trượt → đăng #general → chờ → người phụ trách trả lời) → (mới: hỏi bot → RAG truy hồi KB → trả lời kèm nguồn / tag người nếu không chắc → người phụ trách thêm câu mới vào KB). |
| **Bottleneck** | Độ trễ chờ trả lời + gánh nặng trả lời lặp; gốc rễ là search trượt do diễn đạt khác từ khóa. |
| **Impact** | ~5-8 câu lặp/tuần; chờ 1-3 tiếng; ~35'/tuần của người phụ trách; nguy cơ lan truyền thông tin cũ/sai. |
| **Success Metric** | Median time-to-answer < 5 phút; ≥70% câu lặp trả lời tự động & đúng; trả lời lặp/tuần < 10'; không tăng câu trả lời sai bị báo. |
| **Boundary** | Chỉ câu quy trình công khai; không câu nhạy cảm (điểm, đánh giá, quyết định chưa công bố); không chắc → tag người; không tự quyết thay ban điều hành. |
| **AI intervention point** | Sau khi thành viên hỏi và trước khi câu hỏi rơi vào hàng chờ #general: AI hiểu câu hỏi + truy hồi từ KB curate. |
| **Mức chọn** | Workflow: nền Rule (pinned/structure) + RAG cho phần hiểu & truy hồi + người thật review/cập nhật KB. |
| **Rủi ro & người thật kiểm tra** | Risk: hallucination, trả lời sai mà tự tin, trả lời câu lẽ ra phải để người thật. Kiểm soát: nhãn "🤖 tự động" + nút "không đúng" → tag người; ngưỡng tự tin thấp → tag người; người phụ trách duyệt & cập nhật KB hằng tuần. |

### Bước 6.3 — Final decision

| Câu hỏi | Yes / Not Yet / No | Ghi chú |
|---------|--------------------|---------|
| Actor và workflow đã rõ chưa? | Yes | Cả nhóm hiểu domain, workflow vẽ được |
| Baseline và success metric đã đo được chưa? | Not Yet | Đã đếm log 2 tuần; cần 4-6 tuần để chốt con số |
| Có data/input đủ dùng chưa? | Not Yet | Cần curate KB ban đầu từ pinned + vài doc (vài giờ công) |
| Nếu AI sai, hậu quả có chấp nhận được không? | Yes | Câu quy trình công khai; có nhãn + nút báo sai + boundary cho câu nhạy cảm |
| Có người review/owner vận hành không? | Yes | Ban kỹ thuật duyệt & cập nhật KB |
| Có cách non-AI đơn giản hơn không? | Yes (một phần) | Pinned/Rule là nền, nhưng không giải gốc rễ search trượt |

Decision:

```text
Go với scope nhỏ (pilot bán thủ công).
```

Lý do:
- Problem rõ, workflow rõ, AI nằm ở đúng một bước có giá trị, human review rõ, rủi ro kiểm soát được.
- Metric chưa chốt cứng nên Go ở dạng **pilot có điều kiện**, không cam kết con số trước khi đo đủ.

Nếu Go, pilot nhỏ nhất:

```text
- Curate KB từ ~15-20 câu hỏi quy trình hay gặp nhất (lấy từ log #general 2 tuần) + pinned messages.
- Chạy bán thủ công: dùng một bot RAG có sẵn (vd Wallu/Mava) HOẶC một kênh #ask-bot nơi
  thành viên hỏi và một thành viên ban kỹ thuật dùng prompt chuẩn trả lời nhanh kèm nguồn.
- Đo trong 2-3 tuần: time-to-answer, % trả lời đúng, số lần bấm "không đúng".
- Bot luôn gắn nhãn "🤖 tự động" và có nút báo sai → tag người thật.
```

Nếu Not Yet (điều cần validate trước khi mở rộng):

```text
- Đếm log dài hơn (4-6 tuần) để chốt baseline & target.
- Xác nhận đủ pinned content sạch để làm KB, nếu không thì curate trước.
- Thử với một nhóm nhỏ trước khi bật cho cả server.
```

Nếu No-Go (nếu pilot thất bại — vd >30% câu bị báo "không đúng" 2 tuần liền):

```text
- Hạ về Rule/No-AI: chuẩn hóa kênh + pinned FAQ + một người trực FAQ luân phiên.
- Đây vẫn là cải thiện thật, chỉ là không dùng AI.
```

Decision rationale (tổng):
- Không chọn AI vì "muốn làm AI" — chọn vì search trượt do diễn đạt là chỗ AI thật sự thêm giá trị.
- Có thành phần non-AI (Rule làm nền) và đường quay về rõ ràng.
- AI ở đúng một bước, người thật giữ quyền quyết định và cập nhật nguồn.
