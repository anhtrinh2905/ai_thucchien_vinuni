# 01 — Individual Problem Scan

> Bài cá nhân (Phase 1 + Phase 2). Actor "tôi": sinh viên năm 2 ngành Computer Science tại VinUni, thành viên ban kỹ thuật của một CLB AI khoảng 40 thành viên, đồng thời học nhiều môn có assignment nhóm. Tôi là một trong những người hay được hỏi lại các câu hỏi về quy trình của CLB.

## Phase 1 — Scan rộng (10 problems)

Tôi tự scan trước theo 4 lăng kính, sau đó mới dùng AI để gợi thêm góc nhìn và bỏ các ý không có trải nghiệm thật.

| #  | Lăng kính        | Problem quan sát được                                                                                  | Ai đang đau?                       | Dấu hiệu thật |
|----|------------------|--------------------------------------------------------------------------------------------------------|------------------------------------|---------------|
| 1  | Lặp lại          | Thành viên hỏi lại câu hỏi quy trình trong Discord CLB (deadline, format nộp, link tài liệu) đã trả lời trước đó nhưng trôi mất | Thành viên mới + người phụ trách trả lời | ~5-8 câu lặp/tuần; người hỏi chờ 1-3 tiếng mới có trả lời |
| 2  | Lặp lại          | Mỗi sáng viết standup/update tiến độ assignment nhóm cùng một format                                    | Tôi                                | 5-10 phút/ngày, mỗi ngày |
| 3  | Tốn thời gian    | Đọc 3-5 paper/tài liệu dài để viết phần related work cho báo cáo môn học                                | Sinh viên làm research project     | 45-60 phút/paper |
| 4  | Tốn thời gian    | Tổng hợp ghi chú từ slide + recording + sách thành bộ ôn thi trước kỳ                                   | Sinh viên ôn thi                   | Nhiều giờ/môn, dồn vào tuần cuối |
| 5  | AI có thể tốt hơn | Tìm lại quyết định/chốt cũ trong Discord (ví dụ "đã chốt dùng framework nào", "ai phụ trách phần nào")  | Cả nhóm dự án                      | 10-15 phút/lần tìm, đôi khi không tìm ra |
| 6  | AI có thể tốt hơn | Phân loại email/thông báo từ trường (học vụ, sự kiện, deadline) đang lẫn lộn trong inbox                | Sinh viên                          | Dễ bỏ lỡ deadline vì thông báo bị trôi |
| 7  | Pain từ người khác | Bạn cùng nhóm không rõ task của mình sau buổi họp vì action item ghi không rõ                         | Thành viên nhóm                    | 2-3 lần/dự án phải hỏi lại "task của mình là gì" |
| 8  | Pain từ người khác | Ban tổ chức sự kiện CLB trả lời cùng câu hỏi của người đăng ký (địa điểm, giờ, cần mang gì)            | Ban tổ chức + người tham gia       | Hàng chục DM/comment lặp lại trước mỗi event |
| 9  | Lặp lại          | Tổng hợp feedback Google Form sau mỗi workshop thành report                                             | Ban nội dung CLB                   | 30-45 phút/buổi |
| 10 | Tốn thời gian    | Member mới onboard vào codebase dự án CLB phải tự dò "code ở đâu, chạy thế nào"                         | Member mới + maintainer            | Vài tiếng cho mỗi người mới |

Vì sao phần scan này mạnh:

- Scan rộng (10 > mức tối thiểu 5) trước khi hội tụ.
- Đủ 4 lăng kính, mỗi problem có actor và dấu hiệu thật (thời gian, tần suất, số người).
- Không bắt đầu bằng "làm chatbot" hay "xây agent" — bắt đầu từ workflow và pain.
- Nhiều problem (#1, #5, #8) cùng chỉ về một pattern lớn: **kiến thức bị kẹt trong chat → bị hỏi lại / khó tìm lại**. Đây là tín hiệu tốt cho bước hội tụ nhóm.

## Phase 2 — Chọn top 3

| Rank | Problem                                      | Vì sao chọn                                                                 | Điều còn chưa chắc |
|------|----------------------------------------------|------------------------------------------------------------------------------|--------------------|
| 1    | Câu hỏi quy trình lặp lại trong Discord CLB  | Actor rõ, workflow vẽ được, bottleneck cụ thể (chờ + trả lời lặp), metric đo được, so sánh được No AI/Rule/Workflow/Agent | "Trả lời đúng" đo thế nào; có đủ pinned content để làm KB không |
| 2    | Tổng hợp ghi chú ôn thi từ nhiều nguồn       | Pain thật, lặp lại mỗi kỳ, AI có thể giúp tổng hợp                            | Metric chất lượng khó đo; mỗi người ghi chú một kiểu |
| 3    | Tìm lại quyết định cũ trong Discord          | Nhiều người đau, impact rộng                                                 | Trùng nhiều với #1; data access; scope dễ phình thành "search toàn bộ chat" |

Tôi chọn **#1** làm card chính để pitch, vì nó là bài có workflow rõ nhất và đo được nhất trong một buổi lab.

---

## Problem Card #1 — Câu hỏi quy trình lặp lại trong Discord CLB

```text
┌──────────────────────────────────────────────────────────────┐
│ PROBLEM CARD #1                                                │
│                                                                │
│ Problem 1 câu: Thành viên CLB mất 1-3 tiếng để có câu trả lời  │
│ cho các câu hỏi quy trình lặp lại, vì thông tin cũ trôi mất    │
│ trong Discord và người phụ trách phải trả lời lại bằng tay.    │
│                                                                │
│ Ai đang đau? Thành viên mới (chờ lâu) + người phụ trách        │
│ ban kỹ thuật (trả lời lặp lại mỗi tuần)                        │
│                                                                │
│ Workflow hiện tại:                                             │
│ 1. Cần thông tin → 2. Tự cuộn/search Discord →                │
│ 3. Không thấy, đăng hỏi #general → 4. Chờ người online →      │
│ 5. Người phụ trách tìm lại + trả lời                           │
│                                                                │
│ Bước nghẽn nhất: chờ + trả lời lặp (bước 4-5, ~1-3 tiếng chờ)  │
│                                                                │
│ Đo thành công bằng gì? Median time-to-answer 1-3h → < 5 phút   │
│ cho câu có trong KB; thời gian người phụ trách trả lời lặp     │
│ ~35'/tuần → < 10'/tuần                                         │
│                                                                │
│ Quick gut: □ No AI □ Rule ☑ Workflow □ Agent □ Chưa biết       │
└──────────────────────────────────────────────────────────────┘
```

**Problem 1 câu:**
Thành viên CLB mất khoảng 1-3 tiếng để có câu trả lời cho những câu hỏi quy trình đã được trả lời trước đó, vì thông tin cũ trôi mất trong Discord, và người phụ trách phải trả lời lặp lại bằng tay mỗi tuần.

**Actor:**
Thành viên ban kỹ thuật CLB (người hay được hỏi) và thành viên mới (người hay phải hỏi).

**Thời điểm / bối cảnh:**
Trong tuần, đặc biệt là quanh các mốc deadline đăng ký, nộp bài, và trước mỗi event.

**Current workflow:**

```text
1. Một thành viên cần một thông tin (deadline, format nộp, link tài liệu, quyết định cũ)
2. Tự cuộn lịch sử kênh hoặc dùng search built-in của Discord (~5')
3. Diễn đạt khác từ khóa nên search trượt → đăng câu hỏi vào #general
4. Chờ người phụ trách online và rảnh (median ~1-3 tiếng)
5. Người phụ trách nhớ lại hoặc tự đi tìm nguồn (~5-10') rồi trả lời
6. Câu trả lời lại trôi xuống; vài tuần sau câu hỏi tương tự xuất hiện lại
```

**Bottleneck:**
Bước 4-5. Có hai chi phí cùng lúc: (a) **độ trễ** cho người hỏi (chờ 1-3 tiếng, đôi khi bỏ cuộc), và (b) **thời gian lặp lại** của người phụ trách (trả lời cùng một thứ nhiều lần). Bước 2 (search trượt) là nguyên nhân đẩy việc lên bước 4-5.

**Impact:**
Ước lượng ~5-8 câu hỏi lặp/tuần. Người hỏi chờ trung bình 1-3 tiếng; người phụ trách mất ~30-45 phút/tuần trả lời lại. Tệ hơn độ trễ: vì mỗi người nhớ một kiểu, thông tin cũ/sai (ví dụ deadline đã đổi) bị lan truyền lại.

**Success metric:**
- Median time-to-answer cho câu hỏi quy trình thuộc nhóm FAQ: từ ~1-3 tiếng → **dưới 5 phút**.
- Tỉ lệ câu hỏi lặp được trả lời tự động **và đúng**: mục tiêu **≥ 70%** trong nhóm top FAQ.
- Thời gian người phụ trách trả lời lặp/tuần: ~35' → **dưới 10'**.
- Ràng buộc: **không tăng** số câu trả lời sai bị thành viên báo lại.
- Cách đo baseline: đếm thủ công câu hỏi lặp trong #general trong 2 tuần + tự ghi log thời gian từ lúc hỏi đến lúc có câu trả lời đúng.

**Non-AI alternative:**
Pinned FAQ + cấu trúc kênh rõ + một kênh #announcements chuẩn hóa. Cách này giảm được một phần, nhưng FAQ tĩnh nhanh lỗi thời và người hỏi diễn đạt khác từ khóa nên vẫn search trượt → câu hỏi vẫn quay lại #general.

**AI hypothesis:**
Một bot Q&A theo kiểu RAG (retrieval-augmented generation) chạy trên một knowledge base **nhỏ và được curate** (pinned messages + vài tài liệu chuẩn). Thành viên hỏi bằng ngôn ngữ tự nhiên, bot tìm trong KB và trả lời **kèm trích nguồn/link**; nếu độ tự tin thấp thì **tag người phụ trách** thay vì đoán bừa.

**Quick gut:** Workflow.

### Draft current workflow

```text
CURRENT STATE — người hỏi chờ median ~1-3 tiếng

[1 Cần thông tin]
→ [2 Tự cuộn/search Discord: ~5']        <-- thường trượt vì khác từ khóa
→ [3 Đăng hỏi #general: ~1']
→ [4 Chờ người phụ trách online: ~1-3h]  <-- bottleneck (độ trễ)
→ [5 Người phụ trách tìm + trả lời: ~5-10']  <-- bottleneck (lặp lại)
→ [6 Câu trả lời trôi xuống → vài tuần sau lặp lại]
```

### Draft future workflow

```text
FUTURE STATE — câu trong KB có trả lời < 5 phút

[1 Cần thông tin]
→ [2 Hỏi bot Q&A bằng ngôn ngữ tự nhiên: ~1']
→ [3 Bot tìm trong KB curate (RAG): tự động]
     ├─ Tự tin cao → trả lời kèm link nguồn (< 1')   -- Workflow step
     └─ Tự tin thấp → tag người phụ trách             -- Human boundary
→ [4 Người phụ trách chỉ xử lý câu mới/khó: ~5']      -- Human boundary
→ [5 Người phụ trách thêm câu mới vào KB: ~2']        -- KB tự cập nhật dần

Fallback: bot trả lời sai/không chắc → có nút "không đúng" để
thành viên báo + tự động tag người thật; nếu sai nhiều → hạ về
pinned FAQ thủ công.

Boundary: bot KHÔNG trả lời câu nhạy cảm (điểm, đánh giá cá nhân,
quyết định chưa công bố). Bot KHÔNG tự ra quyết định thay ban điều hành.
```

---

## Problem Cards #2 và #3 — tóm tắt

| Card                         | Actor                  | Bottleneck                                   | Metric                          | Quick gut       | Vì sao chưa chọn làm #1 |
|------------------------------|------------------------|----------------------------------------------|---------------------------------|-----------------|--------------------------|
| Tổng hợp ghi chú ôn thi      | Sinh viên ôn thi       | Biến slide + recording + sách thành bộ ôn có cấu trúc | Nhiều giờ/môn → giảm ~50%        | Workflow        | Quality metric khó đo; mỗi người ghi chú một kiểu nên KB khó chuẩn |
| Tìm lại quyết định cũ Discord | Thành viên nhóm dự án  | Search keyword rồi đọc nhiều thread cũ        | 10-15 phút/lần → dưới 2 phút     | Workflow / Agent | Trùng nhiều với #1; data access và scope dễ phình thành "search toàn bộ lịch sử chat" |

### Card #2 — draft workflow (rút gọn)

```text
CURRENT: [Mở slide] → [Nghe lại recording] → [Đọc sách] → [Tự gõ tổng hợp]  <-- bottleneck
FUTURE:  [Gom nguồn] → [AI tóm tắt theo chương] → [SV chỉnh + bổ sung]  <-- human boundary
Fallback: AI tóm tắt sai trọng tâm → SV tự viết lại phần đó.
```

### Card #3 — draft workflow (rút gọn)

```text
CURRENT: [Nhớ mang máng đã chốt gì] → [Search keyword] → [Đọc nhiều thread] → [Đoán]  <-- bottleneck
FUTURE:  [Hỏi bot] → [Bot trích thread + link gốc] → [Người kiểm lại nguồn]  <-- human boundary
Fallback: bot không tìm thấy → trả "không có trong KB, hỏi <người phụ trách>".
```

---

## Card tôi muốn pitch nhất

**Card #1 — Câu hỏi quy trình lặp lại trong Discord CLB.**

Vì sao: nó có workflow rõ nhất, có baseline đo được trong 2 tuần, cả nhóm đều từng là người hỏi *và* người trả lời nên hiểu domain, và nó cho phép so sánh sạch No AI / Rule / Workflow / Agent.

Câu hỏi tôi muốn nhóm challenge:
- "Trả lời đúng" nên đo thế nào để không bị bot trả lời trôi chảy nhưng sai?
- CLB có đủ pinned content sạch để làm KB ban đầu không, hay phải tốn công curate trước?
- Pinned FAQ thủ công (Rule) đã đủ chưa, có cần AI không?
