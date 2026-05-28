# Ngày 1 — Bài Tập & Phản Ánh

## Nền Tảng LLM API | Phiếu Thực Hành

**Thời lượng:** 1:30 giờ  
**Cấu trúc:** Lập trình cốt lõi (60 phút) → Bài tập mở rộng (30 phút)

---

## Phần 1 — Lập Trình Cốt Lõi (0:00–1:00)

Chạy các ví dụ trong Google Colab tại: [https://colab.research.google.com/drive/172zCiXpLr1FEXMRCAbmZoqTrKiSkUERm?usp=sharing](https://colab.research.google.com/drive/172zCiXpLr1FEXMRCAbmZoqTrKiSkUERm?usp=sharing)

Triển khai tất cả TODO trong `template.py`. Chạy `pytest tests/` để kiểm tra tiến độ.

**Điểm kiểm tra:** Sau khi hoàn thành 4 nhiệm vụ, chạy:

```bash
python template.py
```

Bạn sẽ thấy output so sánh phản hồi của GPT-4o và GPT-4o-mini.

---

## Phần 2 — Bài Tập Mở Rộng (1:00–1:30)

### Bài tập 2.1 — Độ Nhạy Của Temperature

Gọi `call_openai` với các giá trị temperature 0.0, 0.5, 1.0 và 1.5 sử dụng prompt **"Hãy kể cho tôi một sự thật thú vị về Việt Nam."**

**Bạn nhận thấy quy luật gì qua bốn phản hồi?** (2–3 câu)

> Cả bốn phản hồi đều chọn cùng một chủ đề (Hang Sơn Đồng), nhưng mức độ chi tiết và cách diễn đạt thay đổi theo temperature. Ở temperature 0.0 và 0.5, câu trả lời ổn định, tập trung vào các số liệu cốt lõi; khi tăng lên 1.0 và 1.5, model bổ sung thêm chi tiết (tên người phát hiện, hình ảnh so sánh như "tòa nhà 40 tầng") và cách kể linh hoạt hơn. Nhìn chung, temperature càng cao thì phản hồi càng đa dạng và sáng tạo, nhưng vẫn giữ được tính hợp lý với prompt.

**Bạn sẽ đặt temperature bao nhiêu cho chatbot hỗ trợ khách hàng, và tại sao?**

> Tôi sẽ đặt temperature khoảng **0.2–0.4**. Chatbot hỗ trợ khách hàng cần câu trả lời nhất quán, chính xác và dễ dự đoán — ví dụ cùng một câu hỏi về chính sách hoàn tiền nên cho cùng một thông tin cốt lõi. Temperature thấp giúp giảm "sáng tạo" không cần thiết, hạn chế bịa thông tin và giữ giọng điệu chuyên nghiệp, ổn định.

---

### Bài tập 2.2 — Đánh Đổi Chi Phí

Xem xét kịch bản: 10.000 người dùng hoạt động mỗi ngày, mỗi người thực hiện 3 lần gọi API, mỗi lần trung bình ~350 token.

**Ước tính xem GPT-4o đắt hơn GPT-4o-mini bao nhiêu lần cho workload này:**

> Workload: 10.000 × 3 = **30.000 lần gọi/ngày**; ~~350 token/lần → **10,5 triệu token đầu ra/ngày** (~~10.500 đơn vị 1K token). Chi phí GPT-4o: 10.500 × $0,010 = **~$105/ngày**; GPT-4o-mini: 10.500 × $0,0006 = **~$6,30/ngày**. GPT-4o đắt hơn khoảng **16–17 lần** (tỷ lệ giá output: $0,010 / $0,0006 ≈ 16,7×).

**Mô tả một trường hợp mà chi phí cao hơn của GPT-4o là xứng đáng, và một trường hợp GPT-4o-mini là lựa chọn tốt hơn:**

> **GPT-4o xứng đáng** khi cần suy luận phức tạp, độ chính xác cao — ví dụ phân tích hợp đồng pháp lý, chẩn đoán lỗi kỹ thuật nhiều bước, hoặc tư vấn y tế nơi sai sót có hậu quả nghiêm trọng. **GPT-4o-mini phù hợp hơn** cho các tác vụ khối lượng lớn, mẫu lặp lại — như phân loại email, tóm tắt FAQ, gợi ý câu trả lời nhanh trong chatbot hỗ trợ cơ bản, nơi tốc độ và chi phí quan trọng hơn độ tinh vi tối đa.

---

### Bài tập 2.3 — Trải Nghiệm Người Dùng với Streaming

**Streaming quan trọng nhất trong trường hợp nào, và khi nào thì non-streaming lại phù hợp hơn?** (1 đoạn văn)

> Streaming quan trọng nhất khi người dùng tương tác trực tiếp và cần cảm giác phản hồi tức thì — như chatbot hỗ trợ khách hàng (đã thử trong lab: token hiện dần thay vì chờ cả câu), trợ lý viết văn bản dài, hoặc ứng dụng giáo dục. Việc hiển thị từng phần giúp giảm cảm giác chờ (perceived latency), giữ người dùng ở lại và cho phép đọc song song khi model còn đang sinh text. Non-streaming phù hợp hơn khi hệ thống backend cần toàn bộ phản hồi trước khi xử lý tiếp — ví dụ parse JSON có cấu trúc, pipeline tự động (batch job), hoặc khi cần validate/log nội dung đầy đủ trước khi trả về client; lúc đó gọi một lần, nhận kết quả hoàn chỉnh sẽ đơn giản và ổn định hơn.

## Danh Sách Kiểm Tra Nộp Bài

- Tất cả tests pass: `pytest tests/ -v`
- `call_openai` đã triển khai và kiểm thử
- `call_openai_mini` đã triển khai và kiểm thử
- `compare_models` đã triển khai và kiểm thử
- `streaming_chatbot` đã triển khai và kiểm thử
- `retry_with_backoff` đã triển khai và kiểm thử
- `batch_compare` đã triển khai và kiểm thử
- `format_comparison_table` đã triển khai và kiểm thử
- `exercises.md` đã điền đầy đủ
- Sao chép bài làm vào folder `solution` và đặt tên theo quy định

