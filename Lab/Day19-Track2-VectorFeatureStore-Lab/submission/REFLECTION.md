# Reflection — Lab 19

**Tên:** Hồ Thành Tiến
**Cohort:** A20-K2
**Path đã chạy:** lite

---

## Câu hỏi (≤ 200 chữ)

> Trên golden set 50 queries, mode nào thắng ở loại query nào (`exact` /
> `paraphrase` / `mixed`), và tại sao? Khi nào bạn **không** dùng hybrid
> (i.e. khi nào pure BM25 hoặc pure vector là lựa chọn đúng)?

Trên golden set 50 queries, kết quả Precision@10 cho thấy:

- **Exact queries** (15 queries): BM25 = 96.7%, Hybrid = 96.7% — ngang nhau vì từ khóa kỹ thuật xuất hiện verbatim, BM25 đã đủ mạnh.
- **Paraphrase queries** (15 queries): cả ba mode đều yếu (BM25 33.3%, Semantic 24.0%, Hybrid 32.0%) vì embedding model `bge-small-en` không mạnh với tiếng Việt. Dùng `bge-m3` multilingual sẽ cải thiện rõ.
- **Mixed queries** (20 queries): Hybrid = **100%** > Semantic 98.5% > BM25 97.0% — hybrid thắng rõ ràng nhờ kết hợp tín hiệu từ khóa và ngữ nghĩa.

**Khi không dùng hybrid:** (1) Khi latency ngân sách cực thấp (< 5ms) và corpus có từ vựng nhất quán — BM25 thuần nhanh hơn 10× và đủ tốt. (2) Khi query hoàn toàn là ngôn ngữ tự nhiên/câu hỏi dài mà không chứa từ kỹ thuật — vector thuần cho kết quả tốt hơn và không cần maintain BM25 index riêng.

---

## Điều ngạc nhiên nhất khi làm lab này

Điều ngạc nhiên nhất là hybrid không phải lúc nào cũng thắng tuyệt đối — trên exact queries, BM25 thuần đã đạt 96.7% ngang Hybrid, cho thấy RRF chỉ thực sự tạo ra giá trị ở mixed queries. Việc chọn đúng embedding model (multilingual vs English-only) có tác động lớn hơn nhiều so với thuật toán fusion.

---

## Bonus challenge

- [ ] Đã làm bonus (xem `bonus/`)
- [ ] Pair work với: _<tên đồng đội nếu có>_
