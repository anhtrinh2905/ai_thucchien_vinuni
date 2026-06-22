# Failure Analysis — Lab 18: Production RAG

**Nhóm:** Cá nhân  

---

## RAGAS Scores

| Metric | Naive Baseline | Production | Δ |
|--------|---------------|------------|---|
| Faithfulness | 0.8183 | 0.7417 | -0.0767 |
| Answer Relevancy | 0.7213 | 0.7718 | +0.0504 |
| Context Precision | 0.9250 | 0.9417 | +0.0167 |
| Context Recall | 0.9250 | 0.7917 | -0.1333 |

## Bottom-5 Failures

### #1 — Bao lâu phải đổi mật khẩu một lần?
- **Question:** Bao lâu phải đổi mật khẩu một lần?
- **Expected:** Mật khẩu phải thay đổi mỗi **120 ngày** (chính sách v2.0 hiện hành).
- **Got:** Trả lời **90 ngày** (lấy từ `mat_khau_v1.md` — policy cũ).
- **Worst metric:** faithfulness (0.0)
- **Error Tree:** Output sai → Context đúng? **Không** (context chứa v1) → Query OK? Có → Retrieval lấy nhầm version cũ
- **Root cause:** Corpus có 2 version policy (`mat_khau_v1.md` vs `mat_khau_v2.md`); hybrid search không ưu tiên document mới hơn.
- **Suggested fix:** Thêm metadata `version`/`superseded_by` + filter hoặc boost doc mới nhất; hoặc dedup version cũ khi index.

### #2 — Tạm ứng 15 triệu, quá hạn 5 ngày bị phạt bao nhiêu?
- **Question:** Nhân viên tạm ứng 15 triệu, sau 20 ngày mới thanh toán. Bị phạt bao nhiêu?
- **Expected:** Phí 2%/tháng ≈ **50.000 VNĐ** (pro-rata 5 ngày quá hạn trên 15 triệu).
- **Got:** LLM không tính đúng công thức hoặc trả lời thiếu số liệu cụ thể.
- **Worst metric:** faithfulness (0.0)
- **Error Tree:** Output sai → Context đúng? Một phần (context_recall=0.5) → Query OK? Có → LLM không suy luận số học từ context
- **Root cause:** Câu hỏi numeric/multi-hop; context bị cắt nhỏ (child chunk 256 chars) nên thiếu công thức tính phí.
- **Suggested fix:** Dùng parent chunk khi trả lời; hoặc tăng child_size cho section chứa bảng/quy tắc tính toán.

### #3 — Hoàn trả khóa học 25 triệu khi nghỉ sớm
- **Question:** Nhân viên được tài trợ khóa học 25 triệu, nghỉ việc sau 8 tháng. Phải hoàn trả bao nhiêu?
- **Expected:** **25.000.000 VNĐ** (100% vì chưa đủ 1 năm cam kết).
- **Got:** Trả lời không khớp ground truth (faithfulness=0) dù context recall=1.0.
- **Worst metric:** faithfulness (0.0)
- **Error Tree:** Output sai → Context đúng? **Có** → Query OK? Có → **LLM hallucinating / suy luận sai điều kiện cam kết**
- **Root cause:** Prompt quá ngắn, LLM không bám sát điều kiện "1 năm sau hoàn thành khóa học".
- **Suggested fix:** Tighten prompt (yêu cầu trích dẫn điều kiện); temperature=0; chain-of-thought cho câu multi-hop.

### #4 — Mua thiết bị 55 triệu cần ai phê duyệt?
- **Question:** Muốn mua thiết bị trị giá 55 triệu cần ai phê duyệt?
- **Expected:** **Tổng Giám đốc (CEO)** phê duyệt (đơn >50 triệu).
- **Got:** Trả lời đúng faithfulness (1.0) nhưng **context_recall=0** — RAGAS không thấy context chứa ground truth.
- **Worst metric:** context_recall (0.0)
- **Error Tree:** Output đúng? Có → Context đúng? **Không** → Query OK? Có → **Missing relevant chunks**
- **Root cause:** Ngưỡng phê duyệt 50 triệu nằm trong chunk khác với chunk được retrieve; BM25/dense không match "55 triệu" với "trên 50 triệu".
- **Suggested fix:** HyQA enrichment thêm câu hỏi dạng "Ai phê duyệt đơn hàng trên 50 triệu?"; hoặc metadata filter theo category `workflow`.

### #5 — Lương thử việc Junior cao nhất
- **Question:** Lương thử việc của nhân viên Junior mức cao nhất là bao nhiêu?
- **Expected:** **17.000.000 VNĐ/tháng** (85% × 20 triệu).
- **Got:** Trả lời sai phép tính hoặc thiếu bước nhân 85% (faithfulness=0).
- **Worst metric:** faithfulness (0.0)
- **Error Tree:** Output sai → Context đúng? Có (recall=1.0) → Query OK? Có → **LLM không thực hiện phép nhân 85%**
- **Root cause:** Multi-hop numeric — cần 2 facts (Junior max = 20M, thử việc = 85%) nhưng LLM chỉ trả một trong hai.
- **Suggested fix:** Prompt yêu cầu "nếu cần tính toán, nêu rõ các bước"; hoặc tool-use / calculator.

## Case Study (cho presentation)

**Question chọn phân tích:** Bao lâu phải đổi mật khẩu một lần?

**Error Tree walkthrough:**
1. Output đúng? → **Không** (90 ngày thay vì 120 ngày)
2. Context đúng? → **Không** — retrieve `mat_khau_v1.md` thay vì `mat_khau_v2.md`
3. Query rewrite OK? → Query rõ ràng; vấn đề ở **version conflict trong corpus**
4. Fix ở bước: **Indexing** — metadata `is_current=true` + filter; hoặc loại bỏ superseded docs

**Nếu có thêm 1 giờ, sẽ optimize:**
- Thêm version-aware metadata filter trước khi search
- Giảm faithfulness drop bằng prompt "ưu tiên chính sách mới nhất nếu có mâu thuẫn"
- Re-run RAGAS chỉ trên 5 failure cases để validate fix
