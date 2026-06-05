# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Trịnh Thị Lan Anh - 2A202600737
**Nhóm:** Do-it
**Ngày:** 05/06/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**  
High cosine similarity nghĩa là hai vector gần cùng hướng, nên hai câu có nội dung/ngữ nghĩa tương đồng. Giá trị càng gần 1 thì mức độ tương đồng càng cao.

**Ví dụ HIGH similarity:**

- Sentence A: *Jang Won Young bị chỉ trích vì thái độ ở sân bay.*
- Sentence B: *Jang Won Young gây tranh cãi do hành xử thiếu lịch sự tại sân bay.*
- Tại sao tương đồng: Cùng chủ thể, cùng bối cảnh (sân bay), cùng ý chính là bị chỉ trích về thái độ.

**Ví dụ LOW similarity:**

- Sentence A: *Angelababy được bổ nhiệm làm đại sứ di sản văn hóa.*
- Sentence B: *Cách làm bánh tiramisu tại nhà với mascarpone.*
- Tại sao khác: Khác hoàn toàn domain (giải trí vs ẩm thực), gần như không có ý nghĩa giao nhau.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**  
Với text embeddings, hướng vector thường quan trọng hơn độ lớn vector. Cosine similarity đo góc giữa các vector nên ổn định hơn khi độ dài/biên độ embedding thay đổi.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**  
Trình bày phép tính:  

- Step = `chunk_size - overlap = 500 - 50 = 450`  
- Số chunk xấp xỉ: `ceil((10000 - 500) / 450) + 1 = ceil(9500 / 450) + 1 = 22 + 1 = 23`

Đáp án: **23 chunks**

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**  
Khi overlap=100 thì step=400, số chunks tăng lên: `ceil((10000-500)/400)+1 = 25`. Overlap lớn hơn giúp giữ ngữ cảnh qua ranh giới chunk, đổi lại số chunk nhiều hơn và tốn chi phí xử lý/lưu trữ hơn.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Tin tức giải trí/ngôi sao (Kenh14 Star)

**Tại sao nhóm chọn domain này?**  
Domain này có dữ liệu nhiều, cập nhật nhanh, dễ thu thập và có độ đa dạng cao về thực thể (người nổi tiếng, sự kiện, bối cảnh). Đây là môi trường phù hợp để kiểm tra độ nhạy của các strategy chunking vì bài viết dài, nhiều chi tiết và nhiều câu hỏi fact-based.

### Data Inventory


| #   | Tên tài liệu                    | Nguồn             | Số ký tự  | Metadata đã gán                                           |
| --- | ------------------------------- | ----------------- | --------- | --------------------------------------------------------- |
| 1   | `kenh14_star_1tuan_data.md`     | Kenh14 Star crawl | 1,055,521 | `source`, `date_range`, `category`, `article_id`          |
| 2   | `kenh14_star_ragas_eval.md`     | Nhóm tự biên soạn | 5,479     | `id`, `user_input`, `reference`, `reference_context_hint` |
| 3   | `chunking_experiment_report.md` | Nhóm tự biên soạn | 1,987     | `doc_type=report`, `topic=chunking`                       |
| 4   | `rag_system_design.md`          | Nhóm tự biên soạn | 2,391     | `doc_type=notes`, `topic=rag_design`                      |
| 5   | `vector_store_notes.md`         | Nhóm tự biên soạn | 2,123     | `doc_type=notes`, `topic=vector_store`                    |


### Metadata Schema


| Trường metadata       | Kiểu   | Ví dụ giá trị            | Tại sao hữu ích cho retrieval?          |
| --------------------- | ------ | ------------------------ | --------------------------------------- |
| `source`              | string | `kenh14.vn/star`         | Lọc theo nguồn, tránh nhiễu từ tập khác |
| `article_id`          | int    | `108`                    | Truy vấn chính xác theo bài cụ thể      |
| `person`              | string | `Jang Won Young`         | Truy vấn theo thực thể người            |
| `date` / `date_range` | string | `2026-05-29..2026-06-05` | Hỗ trợ câu hỏi theo thời gian           |
| `category`            | string | `Star`                   | Giữ đúng ngữ cảnh domain                |


---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu với `chunk_size=300`:


| Tài liệu                        | Strategy                         | Chunk Count | Avg Length | Preserves Context?    |
| ------------------------------- | -------------------------------- | ----------- | ---------- | --------------------- |
| `kenh14_star_ragas_eval.md`     | FixedSizeChunker (`fixed_size`)  | 21          | 289.5      | Trung bình            |
| `kenh14_star_ragas_eval.md`     | SentenceChunker (`by_sentences`) | 6           | 911.8      | Cao (nhưng chunk dài) |
| `kenh14_star_ragas_eval.md`     | RecursiveChunker (`recursive`)   | 31          | 175.4      | Khá cao               |
| `chunking_experiment_report.md` | FixedSizeChunker (`fixed_size`)  | 8           | 274.6      | Trung bình            |
| `chunking_experiment_report.md` | SentenceChunker (`by_sentences`) | 5           | 395.6      | Cao                   |
| `chunking_experiment_report.md` | RecursiveChunker (`recursive`)   | 14          | 140.0      | Khá cao               |
| `rag_system_design.md`          | FixedSizeChunker (`fixed_size`)  | 9           | 292.3      | Trung bình            |
| `rag_system_design.md`          | SentenceChunker (`by_sentences`) | 5           | 476.0      | Cao                   |
| `rag_system_design.md`          | RecursiveChunker (`recursive`)   | 15          | 157.5      | Khá cao               |


### Strategy Của Tôi

**Loại:** SentenceChunker

**Mô tả cách hoạt động:**  
SentenceChunker tách văn bản theo ranh giới câu (dựa trên dấu kết thúc câu như `.`, `!`, `?`), sau đó gom các câu theo `max_sentences_per_chunk`. Cách này giúp mỗi chunk giữ được ý nghĩa trọn vẹn ở mức câu thay vì cắt giữa chừng theo số ký tự. Nhờ vậy, chunk thường dễ đọc và phù hợp cho truy vấn hỏi-đáp dạng fact.

**Tại sao tôi chọn strategy này cho domain nhóm?**  
Dữ liệu Kenh14 gồm các bài báo dài nhưng thông tin quan trọng thường nằm gọn trong từng câu hoặc cụm vài câu. SentenceChunker giúp giữ đúng ngữ cảnh câu, giảm tình trạng cắt gãy ý và cải thiện độ chính xác khi retrieve cho các câu hỏi fact extraction trong RAG.

### So Sánh: Strategy của tôi vs Baseline


| Tài liệu                    | Strategy                                  | Chunk Count | Avg Length      | Retrieval Quality?                           |
| --------------------------- | ----------------------------------------- | ----------- | --------------- | -------------------------------------------- |
| `kenh14_star_1tuan_data.md` | best baseline - của tôi (SentenceChunker) | 2373        | (phân phối dài) | Recall cao, lấy được nhiều context liên quan |


### So Sánh Với Thành Viên Khác


| Thành viên            | Strategy         | Retrieval Score (/10) | Điểm mạnh                                     | Điểm yếu                       |
| --------------------- | ---------------- | --------------------- | --------------------------------------------- | ------------------------------ |
| Nguyễn Mạnh Quý       | RecursiveChunker | 8.2                   | Câu trả lời bám ngữ cảnh tốt, chunk linh hoạt | Context recall chưa cao        |
| Trịnh Thị Lan Anh     | SentenceChunker  | 8.0                   | Precision/recall tốt với câu hỏi fact         | Chunk dài, có thể dư thông tin |
| Nguyễn Thanh Anh Quân | FixedSizeChunker | 7.5                   | Đơn giản, chạy nhanh, ổn định                 | Dễ cắt gãy ngữ cảnh            |


**Strategy nào tốt nhất cho domain này? Tại sao?**  
Không có strategy thắng tuyệt đối. Nếu ưu tiên độ bám context và chất lượng trả lời thì RecursiveChunker tốt hơn; nếu ưu tiên độ phủ retrieve thì SentenceChunker nổi bật hơn. Với domain báo chí dài, lựa chọn thực tế là dùng RecursiveChunker + tinh chỉnh retrieval để cải thiện recall.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận khi implement các phần chính trong package `src`.

### Chunking Functions

`**SentenceChunker.chunk` — approach:**  
Mình dùng regex dạng `(?<=[.!?])(?:\\s+|\\n+)` để tách câu theo dấu kết thúc câu + khoảng trắng/xuống dòng. Sau đó strip và gom theo `max_sentences_per_chunk`. Edge case xử lý gồm text rỗng, nhiều khoảng trắng liên tiếp, hoặc không có câu hợp lệ.

`**RecursiveChunker.chunk` / `_split` — approach:**  
Hàm `chunk()` gọi `_split()` theo danh sách separator ưu tiên; nếu text đã nhỏ hơn `chunk_size` thì trả luôn. Trong `_split()`, nếu separator hiện tại không tách được thì hạ cấp separator kế tiếp; separator rỗng là base case cắt cứng theo `chunk_size`. Thuật toán dùng buffer để gom phần nhỏ thành chunk hợp lệ trước khi append.

### EmbeddingStore

`**add_documents` + `search` — approach:**  
Mỗi document được normalize thành record chứa `id`, `content`, `metadata`, `embedding`. Với in-memory mode, search tính dot-product giữa embedding query và embedding chunk, sắp xếp giảm dần theo score rồi lấy top-k. Với Chroma mode, dùng `collection.add()` và `collection.query()`.

`**search_with_filter` + `delete_document` — approach:**  
`search_with_filter()` lọc metadata trước, sau đó mới chạy similarity search trên tập đã lọc. `delete_document()` xóa tất cả chunks theo `metadata['doc_id']`; trả về boolean để biết có xóa thành công hay không. Cách này nhất quán cho cả in-memory và Chroma.

### KnowledgeBaseAgent

`**answer` — approach:**  
Agent retrieve top-k chunks từ store, ghép thành context theo format rõ ràng rồi tạo prompt "chỉ trả lời dựa trên context". Nếu không đủ context, prompt yêu cầu model nêu rõ thiếu dữ liệu. Cấu trúc này giúp giảm hallucination và tăng tính grounded cho câu trả lời.

### Test Results

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.14, pytest-9.0.3
collecting ... collected 42 items
...
============================== 42 passed in 0.03s ==============================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)


| Pair | Sentence A                                                                  | Sentence B                                                           | Dự đoán | Actual Score | Đúng? |
| ---- | --------------------------------------------------------------------------- | -------------------------------------------------------------------- | ------- | ------------ | ----- |
| 1    | Bài viết nói về scandal của Jang Won Young ở sân bay.                       | Jang Won Young bị chỉ trích vì thái độ ở sân bay.                    | high    | -0.210       | Sai   |
| 2    | Angelababy được bổ nhiệm đại sứ di sản văn hóa phi vật thể.                 | Tin vui của Angelababy là được bổ nhiệm làm đại sứ quảng bá di sản.  | high    | -0.020       | Sai   |
| 3    | Thời tiết Hà Nội hôm nay mưa to và gió lớn.                                 | Hề Mộng Dao đeo 103,7 carat kim cương trước đám cưới.                | low     | -0.040       | Đúng  |
| 4    | Recursive chunking giữ ngữ nghĩa tốt hơn fixed-size trong nhiều trường hợp. | Chunking theo đệ quy thường giúp bảo toàn ngữ cảnh tốt hơn cắt cứng. | high    | -0.055       | Sai   |
| 5    | Bóng đá Việt Nam thắng trận chung kết AFF Cup.                              | Cách làm bánh tiramisu tại nhà với mascarpone.                       | low     | -0.263       | Đúng  |


**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**  
Bất ngờ nhất là cặp 2 và 4 có nghĩa gần nhau nhưng điểm vẫn thấp/âm với mock embedding. Điều này cho thấy backend `_mock_embed` chỉ mang tính deterministic để test kỹ thuật, không phản ánh ngữ nghĩa thật như embedding model production.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân trong package `src`. 5 queries trùng với bộ câu hỏi nhóm thống nhất.

### Benchmark Queries & Gold Answers (nhóm thống nhất)


| #   | Query                                                                       | Gold Answer                                                                                            |
| --- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| 1   | Trong tuần được thu thập, chuyên mục Star của Kenh14 có bao nhiêu bài viết? | File tổng hợp ghi nhận 206 bài viết trong khoảng thời gian từ 2026-05-29 đến 2026-06-05.               |
| 2   | Vì sao Jang Ga Hyun bức xúc đăng bài trên trang cá nhân?                    | Vì tài xế nhắn tin rồi chuyển sang chửi bới, đe dọa tung clip riêng tư khi cô không phản hồi.          |
| 3   | Jang Won Young bị chỉ trích vì hành động gì ở sân bay?                      | Không hợp tác khi được yêu cầu tháo khẩu trang, nhận hộ chiếu bằng một tay và bị cho là thiếu lịch sự. |
| 4   | Tin vui mới của Angelababy trong bài viết là gì?                            | Cô được bổ nhiệm làm đại sứ quảng bá di sản văn hóa phi vật thể huyện Lôi Sơn, tỉnh Quý Châu.          |
| 5   | Hề Mộng Dao gây chú ý vì chi tiết xa hoa nào trước đám cưới?                | Đeo tổng cộng khoảng 103,7 carat kim cương, trị giá ước tính khoảng 49 triệu NDT.                      |


### Kết Quả Của Tôi


| #   | Query | Top-1 Retrieved Chunk (tóm tắt)                                       | Score        | Relevant? | Agent Answer (tóm tắt)                                                      |
| --- | ----- | --------------------------------------------------------------------- | ------------ | --------- | --------------------------------------------------------------------------- |
| 1   | q1    | Header thống kê đầu file có thông tin tổng số bài và khoảng thời gian | lexical rank | Có        | Trả lời đúng: 206 bài trong khung 2026-05-29 đến 2026-06-05                 |
| 2   | q2    | Cụm bài 1 về Jang Ga Hyun và tài xế đe dọa clip riêng tư              | lexical rank | Có        | Trả lời đúng trọng tâm lý do bức xúc                                        |
| 3   | q3    | Cụm bài 2 về hành vi ở sân bay của Jang Won Young                     | lexical rank | Có        | Trả lời đúng 3 ý: không hợp tác, nhận hộ chiếu 1 tay, thái độ thiếu lịch sự |
| 4   | q4    | Cụm bài 3 về tin vui Angelababy được bổ nhiệm                         | lexical rank | Có        | Trả lời đúng nội dung bổ nhiệm đại sứ                                       |
| 5   | q5    | Cụm bài về Hề Mộng Dao và lượng kim cương 103,7 carat                 | lexical rank | Có        | Trả lời đúng chi tiết xa hoa chính                                          |


**Bao nhiêu queries trả về chunk relevant trong top-3?** 5 / 5

### RAGAS So Sánh 3 Chunking Methods

Notebook chạy đánh giá: `report/ragas_chunking_evaluation.ipynb`  
File kết quả raw: `report/ragas_chunking_eval_results.json`


| Strategy         | Chunk Count | Faithfulness (avg) | Answer Relevancy (avg) | Context Precision (avg) | Context Recall (avg) |
| ---------------- | ----------- | ------------------ | ---------------------- | ----------------------- | -------------------- |
| FixedSizeChunker | 2346        | 0.600              | 0.526                  | 0.640                   | 0.733                |
| SentenceChunker  | 2373        | 0.550              | 0.517                  | 0.690                   | 0.800                |
| RecursiveChunker | 2948        | 0.760              | 0.611                  | 0.500                   | 0.300                |


Nhận xét nhanh:

- `RecursiveChunker` cho `faithfulness` và `answer_relevancy` trung bình cao nhất, nhưng `context_precision` và `context_recall` thấp hơn.
- `SentenceChunker` có `context_precision` và `context_recall` cao nhất trong lần chạy này.
- `FixedSizeChunker` cho kết quả cân bằng, không vượt trội tuyệt đối nhưng ổn định.

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**  
Mình học được cách dùng metadata filter rõ ràng (`article_id`, `person`) để giảm nhiễu trước khi ranking. Cách làm này cải thiện đáng kể độ chính xác khi câu hỏi nhắm vào một nhân vật cụ thể.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**  
Nhóm khác trình bày rất tốt việc tách riêng pipeline thành `retrieve -> generate -> evaluate`, nhờ đó debug từng bước dễ hơn. Đặc biệt, việc log top contexts giúp phát hiện lỗi chunking/tokenization rất nhanh.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**  
Mình sẽ chuẩn hóa metadata ngay từ lúc tiền xử lý (đặc biệt là `article_id`, `title`, `person`) và ưu tiên chunk theo ranh giới tiêu đề/phần nội dung. Mình cũng sẽ thêm bước cleaning để tách các câu bị dính dấu câu nhằm tăng chất lượng retrieve.

---

## Tự Đánh Giá


| Tiêu chí                    | Loại    | Điểm tự đánh giá |
| --------------------------- | ------- | ---------------- |
| Warm-up                     | Cá nhân | 5 / 5            |
| Document selection          | Nhóm    | 10 / 10          |
| Chunking strategy           | Nhóm    | 13 / 15          |
| My approach                 | Cá nhân | 10 / 10          |
| Similarity predictions      | Cá nhân | 4 / 5            |
| Results                     | Cá nhân | 9 / 10           |
| Core implementation (tests) | Cá nhân | 30 / 30          |
| Demo                        | Nhóm    | 5 / 5            |
| **Tổng**                    |         | **86 / 100**     |


