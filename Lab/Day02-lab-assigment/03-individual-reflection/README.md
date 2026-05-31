# 03 — Individual Reflection

> ⚠️ **Đọc trước khi nộp:** Worksheet ghi rõ reflection là phần **cá nhân** và **không được để AI viết thay**. Phần dưới đây là *khung + ví dụ* để bạn thấy một reflection tốt gồm những gì. **Hãy thay toàn bộ nội dung bằng trải nghiệm thật của bạn** trong buổi lab — bạn đã làm gì, AI giúp/sai ở đâu, bạn sửa gì. Nếu nộp nguyên văn ví dụ này, reflection sẽ không phản ánh đúng đóng góp của bạn và sẽ mất điểm (mục "Reflection cá nhân" 10đ + "Kiểm tra hiểu bài" 6đ).

---

## Tôi đã tham gia vào phần nào? (ví dụ — Khoa)

| Hoạt động | Tôi đã làm gì? | Kết quả / ảnh hưởng |
|-----------|----------------|---------------------|
| Scan cá nhân | Đưa ra 10 problems, nhiều ý quanh "kiến thức kẹt trong chat" | Nhóm có cụm A để hội tụ |
| Pitch Problem Card | Pitch card #1 (Discord repeated questions) | Vào shortlist, được chọn |
| Challenge bài bạn khác | Hỏi An: "bài form feedback có bao nhiêu người thật sự gặp?" | Nhóm thấy impact của B hẹp |
| Gom trùng / cluster | Đề xuất gộp 1+4+11 thành một cụm | Tránh tách nhỏ pain giống nhau |
| Chọn candidate problem | Lập luận chọn A theo "hiểu domain + so sánh R/W/A" | Nhóm đồng thuận chọn A |
| Validation / research | Đếm log #general 2 tuần; tìm Wallu, Mava, BetaHub, RAG IBM/Azure | Nhóm thấy không cần build agent từ đầu |
| Workflow nhóm | Vẽ current/future workflow + đánh dấu boundary/fallback | Dùng làm workflow bản cuối |
| Problem Statement | Viết draft v0, nhóm sửa thành v1 | Thu hẹp scope về "câu công khai" |
| Rule / Workflow / Agent | Lập luận chọn Workflow, bác Agent vì rủi ro privacy | Nhóm thống nhất mức |
| Decision | Đề xuất "Go scope nhỏ + điều kiện" thay vì Go thẳng | Quyết định thận trọng hơn |

## Bảng dùng AI trong reflection (ví dụ)

| Phase | Tôi dùng AI để làm gì? | AI hữu ích ở đâu? | AI sai/hời hợt ở đâu? | Tôi sửa gì bằng nhận định của mình |
|-------|------------------------|-------------------|------------------------|-------------------------------------|
| Scan | Gợi thêm problem theo vai trò member CLB | Nhắc tôi nhớ ra bài onboard codebase, phân loại email | Một số gợi ý quá rộng ("trợ lý AI cho CLB") | Bỏ các ý không có workflow/dấu hiệu thật |
| Problem Card | Nhờ AI đóng vai PM hoài nghi phản biện | Chỉ ra metric "trả lời đúng" của tôi còn mơ hồ | AI khen nhiều hơn chê khi tôi không yêu cầu rõ | Đổi prompt "chỉ ra điểm yếu, đừng khen", rồi tự thêm cách đo "đúng" |
| Workflow | Nhờ AI chuyển mô tả thành sơ đồ | Vẽ nhánh nhanh hơn | AI gộp bước "tag người" vào "trả lời" | Tách lại vì human boundary phải tách bạch |
| Research | Tìm tool tương tự + giải thích RAG | Tìm ra Wallu/Mava/BetaHub, khái niệm similarity≠relevance | Có claim "giảm 70-80%" không nguồn rõ | Đánh dấu là *vendor-claimed*, không dùng làm metric |
| Problem Statement | Nhờ AI soi field mơ hồ | Chỉ ra boundary chưa nói câu nhạy cảm | AI gợi ý nhảy lên Agent | Giữ ở Workflow, viết rõ boundary câu nhạy cảm |
| Rule/Workflow/Agent | Hỏi phản biện vì sao không Agent | Liệt kê rủi ro privacy của Agent | AI vẫn nghiêng "Agent xịn hơn" | Tự chốt Workflow theo luồng thật của bài |
| Decision | Hỏi rủi ro của Go thẳng | Gợi ý cần baseline dài hơn | — | Đổi thành "Go scope nhỏ + điều kiện rollback" |

## Reflection (ví dụ — thay bằng của bạn)

```text
Điều tôi học rõ nhất là problem tốt không phải problem nghe "AI" nhất, mà là problem
có workflow và metric rõ. Lúc đầu cả nhóm dễ bị cuốn vào "xây một con bot cho CLB" —
đó là solution-first. Khi tôi đếm log #general thật, tôi mới thấy pain không phải
"thiếu thông tin" mà là độ trễ và search trượt vì diễn đạt. Cái đó đổi hẳn cách viết
Problem Statement: chúng tôi thu hẹp về "câu quy trình công khai, lặp lại".

Có một lúc tôi bị challenge và đổi ý: tôi từng nghĩ phải để bot trả lời mọi câu cho
"ngầu", nhưng một bạn trong nhóm chỉ ra phần lớn câu khó lại là câu nhạy cảm (điểm,
quyết định chưa công bố). Tôi đồng ý thêm boundary loại các câu đó ra. Đây là chỗ tôi
thấy mình quyết định tốt hơn nhờ nghe người khác.

AI hữu ích để phản biện và vẽ nhanh, nhưng tôi học được phải prompt rõ ("chỉ ra điểm
yếu") và tự kiểm nguồn — AI có lúc khen quá và đẩy tôi lên Agent quá sớm. Phần research
cũng dạy tôi rằng nhiều sản phẩm tốt đều theo cùng một pattern: AI draft/trả lời, người
thật review và cập nhật nguồn.

Nếu làm lại, tôi sẽ đếm log dài hơn (4-6 tuần) trước khi nói con số "1-3 tiếng → 5 phút",
vì baseline 2 tuần còn mỏng. Tôi cũng sẽ challenge nhóm sớm hơn ở chỗ "đo trả lời ĐÚNG
thế nào", vì đó là field yếu nhất của bài.
```

## Tự kiểm hiểu bài (mạch một dòng)

```text
Problem: member + người phụ trách mất thời gian vì câu hỏi quy trình lặp lại, thông tin trôi mất
→ Workflow: hỏi → search trượt → đăng #general → chờ → trả lời lặp
→ Metric: time-to-answer < 5', ≥70% câu lặp trả lời đúng, trả lời lặp/tuần < 10'
→ Boundary: chỉ câu công khai, không câu nhạy cảm, không chắc thì tag người
→ Độ phù hợp AI: Workflow (RAG hỗ trợ 1 bước hiểu+truy hồi), không Agent vì luồng cố định + rủi ro privacy
→ Decision: Go scope nhỏ + điều kiện, rollback về Rule nếu sai nhiều.
```

Vì sao nhóm chọn **Workflow** chứ không Rule/Agent: Rule khớp từ khóa không giải gốc rễ (diễn đạt khác từ khóa); Agent thừa vì không có bước nào cần AI tự lập kế hoạch, lại thêm rủi ro privacy. Vì sao **Go scope nhỏ**: rủi ro kiểm soát được và có đường quay về, nhưng baseline metric chưa đo đủ nên chưa cam kết con số.
