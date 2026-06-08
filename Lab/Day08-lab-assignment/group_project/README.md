# Group Project — Requirement 1 (RAG Chatbot bằng Streamlit)

Triển khai này hoàn thành **Yêu cầu 1**:
- Streamlit chat UI
- Câu trả lời có citation
- Cho phép chọn splitter / embedding model / reranking
- Cho phép chọn vector store: `local_numpy` hoặc `weaviate_cloud`
- Hỗ trợ follow-up questions với conversation memory
- Hiển thị source documents được dùng khi trả lời

## Kiến trúc

```text
Streamlit UI
  -> Configurable RAG backend (group_project/rag_chatbot.py)
  -> Chunking (Recursive | MarkdownHeader | Semantic)
  -> Embedding (text-embedding-3-small | text-embedding-3-large)
  -> Vector store (local_numpy hoặc Weaviate Cloud) + Hybrid retrieval (Semantic + BM25)
  -> Rerank (none | rrf | mmr | cross_encoder)
  -> LLM generation with citations
  -> Source panel (metadata + chunk content)
```

## Files chính

- `group_project/app.py`: Streamlit app
- `group_project/rag_chatbot.py`: backend RAG configurable

## Điều kiện môi trường

Điền các biến này trong `.env`:

```bash
OPENAI_API_KEY=...
WEAVIATE_URL=https://<cluster>.weaviate.network
WEAVIATE_API_KEY=...
```

Nếu chỉ dùng `local_numpy`, bạn chỉ cần `OPENAI_API_KEY`.

## Chạy ứng dụng

Từ thư mục `Lab/Day08-lab-assignment`:

```bash
pip install -r requirements.txt
streamlit run group_project/app.py
```

## Cách demo nhanh

1. Mở sidebar, chọn:
   - Splitter
   - Embedding model
   - Reranking method
   - Chunk size / overlap / threshold / top-k
2. Bấm `Build/Rebuild Weaviate index`.
3. Đặt câu hỏi trong chat.
4. Xem:
   - Câu trả lời có citation trong nội dung
   - `Retrieval query` (khi bật conversation memory)
   - Panel `Source documents đã dùng` để kiểm tra evidence

## Ghi chú về citation

- Prompt generation bắt buộc mỗi claim có trích dẫn `[source]`.
- Nếu thiếu bằng chứng từ context, chatbot trả về:
  `Tôi không thể xác minh thông tin này từ nguồn hiện có.`
