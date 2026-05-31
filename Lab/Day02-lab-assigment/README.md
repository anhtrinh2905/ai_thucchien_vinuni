# Day 02 Lab — Bản nộp cá nhân

> Bài toán nhóm chọn: **Câu hỏi quy trình bị hỏi lặp lại trong Discord CLB vì thông tin trôi mất.**
> Mức chọn: **Workflow** (bot Q&A theo kiểu RAG trên một knowledge base nhỏ được curate, có người thật kiểm tra). Quyết định: **Go với scope nhỏ (pilot bán thủ công)**.

## ⚠️ Lưu ý quan trọng trước khi nộp

Repo này là một **bản mẫu hoàn chỉnh** đi đúng theo worksheet Day 02. Trước khi nộp thật, bạn cần làm 3 việc:

1. **Đổi tên thư mục gốc** `Day02-XXXXXXXX-HoVaTen` thành mã học viên + tên thật của bạn, ví dụ `Day02-V2024001-NguyenVanA`.
2. **Thay số liệu validation bằng dữ liệu thật của nhóm bạn.** Phần interview/poll trong `02-group-problem-statement` ghi rõ đây là giả định cần kiểm chứng. Worksheet yêu cầu không dùng số liệu không verify được.
3. **Viết lại `03-individual-reflection` bằng trải nghiệm thật của bạn.** Worksheet nói rõ reflection và pitch/challenge **không được để AI viết thay**. Phần reflection ở đây chỉ là *khung gợi ý cấu trúc* — nội dung phải là của chính bạn.

## Cấu trúc repo

```text
Day02-XXXXXXXX-HoVaTen/
├── README.md
├── 01-individual-problem-scan/      # bài cá nhân
│   └── README.md
├── 02-group-problem-statement/      # bản nộp nhóm (copy vào repo cá nhân)
│   └── README.md
└── 03-individual-reflection/        # reflection cá nhân
    └── README.md
```

## Đọc theo thứ tự

1. `01-individual-problem-scan/` — scan 10 problems, top 3 Problem Cards, draft workflow trước/sau cho top 3.
2. `02-group-problem-statement/` — nhật ký hội tụ, validation, research giải pháp thật, workflow trước/sau, Problem Statement v0/v1, so sánh Rule/Workflow/Agent, quyết định cuối.
3. `03-individual-reflection/` — vai trò trong nhóm, cách dùng AI, bài học, nếu làm lại sẽ đổi gì.

## Mạch lập luận một dòng

Người mới + người phụ trách trong Discord CLB mất thời gian vì **câu hỏi quy trình bị hỏi lặp lại và thông tin trôi mất** → bottleneck là *chờ trả lời* và *trả lời lặp lại* → metric là *time-to-answer* và *thời gian trả lời lặp/tuần* → boundary là *bot không trả lời câu nhạy cảm, không chắc thì tag người thật* → AI phù hợp ở mức **Workflow** (RAG trên KB curate, có review), chưa cần Agent → **Go scope nhỏ** vì rủi ro kiểm soát được và có phương án quay về Rule.
