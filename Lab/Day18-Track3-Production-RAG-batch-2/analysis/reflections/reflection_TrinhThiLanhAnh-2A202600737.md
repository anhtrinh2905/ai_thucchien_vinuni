# Individual Reflection — Lab 18

**Tên:** Trinh Thi Lan Anh  - 2A202600737
**Module phụ trách:** M1–M5 (toàn bộ pipeline)

---

## Phần 1: Mapping bài giảng → Code

| Lecture Concept | Module | Hàm cụ thể | Observation |
|----------------|--------|-------------|-------------|
| Semantic chunking | M1 | `chunk_semantic()` | Threshold 0.85 tạo ít chunk hơn basic vì gộp câu cùng chủ đề; threshold 0.5 cho test set nhỏ tạo ~4 chunks vs basic ~6 |
| Hierarchical chunking | M1 | `chunk_hierarchical()` | Parent 2048 + child 256 → 100 children từ 26 docs; retrieve child, trả parent cho LLM |
| Structure-aware chunking | M1 | `chunk_structure_aware()` | Parse `##` headers → mỗi section 1 chunk, metadata có `section` |
| BM25 + Dense fusion | M2 | `reciprocal_rank_fusion()` | RRF (k=60) merge BM25 + dense; doc xuất hiện cả 2 list được boost |
| Vietnamese segmentation | M2 | `segment_vietnamese()` | underthesea + replace `_` → BM25 match "nghỉ phép" đúng |
| Cross-encoder reranking | M3 | `CrossEncoderReranker.rerank()` | bge-reranker-v2-m3 ~300ms/3 docs; "nghỉ phép" rank #1 trước "VPN" |
| RAGAS 4 metrics | M4 | `evaluate_ragas()` | Context precision cao nhất (0.94); faithfulness thấp nhất (0.74) vì version conflict + numeric hallucination |
| Contextual embeddings | M5 | `_enrich_single_call()` | 1 API call/chunk thêm context line trước text; fallback extractive khi API fail |
| Failure diagnostic tree | M4 | `failure_analysis()` | Bottom-5 sorted by avg metric; map worst_metric → diagnosis + fix |

## Phần 2: Khó khăn & giải quyết

**Lỗi gặp phải:**
- `Expecting value: line 1 column 1 (char 0)` — OpenAI trả JSON wrapped trong markdown code block, `json.loads()` fail.
- `No module named pytest` — venv thiếu pytest.
- PDF scan (`BCTC.pdf`, `Nghi_dinh_13-2023.pdf`) không có text layer → bỏ qua với warning.

**Cách debug:**
- Chạy `pytest tests/test_m*.py -v` từng module để isolate lỗi.
- `docker compose up -d` trước khi test dense search / pipeline.
- Đọc `pipeline_run.log` để trace enrichment failures và RAGAS scores.

**Kiến thức thiếu → bổ sung:**
- Version conflict trong RAG corpus → học thêm metadata filtering và document freshness scoring.
- RAGAS faithfulness vs context_recall trade-off → đọc Diagnostic Tree trong lecture slides.

## Phần 3: Action Plan cho project

## Project: HR Policy Chatbot (VinUni internal)

### Hiện tại
- RAG pipeline: basic paragraph chunk + dense search (Qdrant + bge-m3)
- Known issues: trả lời policy cũ khi có 2 version; câu hỏi tính toán (lương, phí) sai

### Plan áp dụng
1. [ ] **Chunking:** Hierarchical (parent 2048 / child 256) + structure-aware cho markdown HR docs
2. [ ] **Search:** Hybrid BM25 (underthesea) + Dense + RRF — BM25 tốt cho keyword tiếng Việt
3. [ ] **Reranking:** CrossEncoder bge-reranker-v2-m3, top-20 → top-3
4. [ ] **Evaluation:** RAGAS 4 metrics + failure_analysis bottom-5 mỗi sprint
5. [ ] **Enrichment:** Combined single-call (summary + HyQA + context prepend) trước khi embed

### Timeline
- **Tuần 1:** Deploy hierarchical chunking + version metadata (`is_current`, `superseded_by`)
- **Tuần 2:** Hybrid search + reranker; baseline RAGAS trên 20 test questions
- **Tuần 3:** Enrichment pipeline + prompt tuning cho numeric/multi-hop questions
- **Tuần 4:** Production A/B test naive vs production; failure analysis review với team HR

---

## Tự đánh giá

| Tiêu chí | Tự chấm (1-5) |
|----------|---------------|
| Hiểu bài giảng | 5 |
| Code quality | 5 |
| Teamwork | N/A (cá nhân) |
| Problem solving | 5 |
