# Kenh14 Star - RAGAS Evaluation Set

File này chứa 5 câu hỏi benchmark dùng cho RAG/RAGAS evaluation trên dữ liệu `kenh14_star_1tuan_data.md`.

## Dataset Schema

Các cột bên dưới có thể map sang RAGAS như sau:

| Cột trong file | Ý nghĩa | Cột RAGAS gợi ý |
|---|---|---|
| `id` | Mã câu hỏi | metadata |
| `user_input` | Câu hỏi người dùng | `user_input` hoặc `question` |
| `reference` | Câu trả lời đúng mong đợi | `reference` hoặc `ground_truth` |
| `reference_context_hint` | Bài/chunk chứa thông tin đúng | dùng để kiểm tra `retrieved_contexts` |
| `metadata_filter` | Filter gợi ý khi retrieve | metadata/filter |

Khi chạy RAGAS thật, pipeline cần sinh thêm:

```text
response           -> câu trả lời do RAG agent tạo
retrieved_contexts -> danh sách chunk mà retriever lấy được
```

---

## Evaluation Questions

| id | user_input | reference | reference_context_hint | metadata_filter |
|---|---|---|---|---|
| q1 | Trong tuần được thu thập, chuyên mục Star của Kenh14 có bao nhiêu bài viết? | File tổng hợp ghi nhận 206 bài viết trong khoảng thời gian từ 2026-05-29 đến 2026-06-05. | Phần thống kê đầu file, dòng "Tổng số bài: 206" và "Khoảng thời gian: 2026-05-29 to 2026-06-05". | `{"source": "kenh14.vn/star"}` |
| q2 | Vì sao Jang Ga Hyun bức xúc đăng bài trên trang cá nhân? | Jang Ga Hyun bức xúc vì một tài xế nhắn tin cho cô, sau đó chuyển sang chửi bới và đe dọa tung clip riêng tư khi cô không trả lời tin nhắn. | Bài 1: "Tình cảnh ngặt nghèo của nữ diễn viên không trả lời tin nhắn, liền bị tài xế dọa tung clip riêng tư". | `{"article_id": 1, "person": "Jang Ga Hyun"}` |
| q3 | Jang Won Young bị chỉ trích vì hành động gì ở sân bay? | Jang Won Young bị chỉ trích vì không hợp tác khi nhân viên sân bay yêu cầu tháo khẩu trang để kiểm tra gương mặt, lấy lại hộ chiếu bằng một tay và rời đi với thái độ bị cho là thiếu lịch sự. | Bài 2: "21,3 triệu người xem Công chúa Kpop ngúng nguẩy, công khai thái độ với nhân viên sân bay". | `{"article_id": 2, "person": "Jang Won Young"}` |
| q4 | Tin vui mới của Angelababy trong bài viết là gì? | Angelababy được bổ nhiệm làm đại sứ quảng bá di sản văn hóa phi vật thể huyện Lôi Sơn, tỉnh Quý Châu, được xem là tín hiệu giúp cô cải thiện hình ảnh và có thêm cơ hội công việc. | Bài 3: "Angelababy có tin vui". | `{"article_id": 3, "person": "Angelababy"}` |
| q5 | Hề Mộng Dao gây chú ý vì chi tiết xa hoa nào trước đám cưới? | Hề Mộng Dao gây chú ý khi đeo tổng cộng khoảng 103,7 carat kim cương, được ước tính trị giá khoảng 49 triệu NDT, gần 180 tỷ đồng. | Bài 108: "Trước giờ G đám cưới hào môn chấn động showbiz..." | `{"article_id": 108, "person": "Hề Mộng Dao"}` |

---

## JSONL Copy For RAGAS Preprocessing

Nếu muốn parse nhanh bằng Python, có thể đọc các dòng JSONL dưới đây và sau đó thêm `response` + `retrieved_contexts` từ hệ thống RAG của nhóm.

```jsonl
{"id":"q1","user_input":"Trong tuần được thu thập, chuyên mục Star của Kenh14 có bao nhiêu bài viết?","reference":"File tổng hợp ghi nhận 206 bài viết trong khoảng thời gian từ 2026-05-29 đến 2026-06-05.","reference_context_hint":"Phần thống kê đầu file, dòng Tổng số bài: 206 và Khoảng thời gian: 2026-05-29 to 2026-06-05.","metadata_filter":{"source":"kenh14.vn/star"}}
{"id":"q2","user_input":"Vì sao Jang Ga Hyun bức xúc đăng bài trên trang cá nhân?","reference":"Jang Ga Hyun bức xúc vì một tài xế nhắn tin cho cô, sau đó chuyển sang chửi bới và đe dọa tung clip riêng tư khi cô không trả lời tin nhắn.","reference_context_hint":"Bài 1: Tình cảnh ngặt nghèo của nữ diễn viên không trả lời tin nhắn, liền bị tài xế dọa tung clip riêng tư.","metadata_filter":{"article_id":1,"person":"Jang Ga Hyun"}}
{"id":"q3","user_input":"Jang Won Young bị chỉ trích vì hành động gì ở sân bay?","reference":"Jang Won Young bị chỉ trích vì không hợp tác khi nhân viên sân bay yêu cầu tháo khẩu trang để kiểm tra gương mặt, lấy lại hộ chiếu bằng một tay và rời đi với thái độ bị cho là thiếu lịch sự.","reference_context_hint":"Bài 2: 21,3 triệu người xem Công chúa Kpop ngúng nguẩy, công khai thái độ với nhân viên sân bay.","metadata_filter":{"article_id":2,"person":"Jang Won Young"}}
{"id":"q4","user_input":"Tin vui mới của Angelababy trong bài viết là gì?","reference":"Angelababy được bổ nhiệm làm đại sứ quảng bá di sản văn hóa phi vật thể huyện Lôi Sơn, tỉnh Quý Châu, được xem là tín hiệu giúp cô cải thiện hình ảnh và có thêm cơ hội công việc.","reference_context_hint":"Bài 3: Angelababy có tin vui.","metadata_filter":{"article_id":3,"person":"Angelababy"}}
{"id":"q5","user_input":"Hề Mộng Dao gây chú ý vì chi tiết xa hoa nào trước đám cưới?","reference":"Hề Mộng Dao gây chú ý khi đeo tổng cộng khoảng 103,7 carat kim cương, được ước tính trị giá khoảng 49 triệu NDT, gần 180 tỷ đồng.","reference_context_hint":"Bài 108: Trước giờ G đám cưới hào môn chấn động showbiz.","metadata_filter":{"article_id":108,"person":"Hề Mộng Dao"}}
```

---

## Python Mapping Example

```python
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

# Sau khi chạy RAG pipeline, mỗi item cần có:
# user_input: câu hỏi
# response: câu trả lời agent sinh ra
# retrieved_contexts: list[str] các chunk được retrieve
# reference: gold answer trong file này

dataset = Dataset.from_list(rows)

result = evaluate(
    dataset,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    ],
)

print(result)
```
