from __future__ import annotations

import json
import math
import os
from pathlib import Path
import re
import sys
from statistics import mean, median
import types

import streamlit as st  # type: ignore[import-not-found]
from dotenv import load_dotenv

from src.chunking import FixedSizeChunker, RecursiveChunker, SentenceChunker

DATA_PATH = Path("data/kenh14_star_1tuan_data.md")
EVAL_PATH = Path("data/kenh14_star_ragas_eval.md")
DEFAULT_CHAT_MODEL = "gpt-4o"


@st.cache_data(show_spinner=False)
def load_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_noi_dung_blocks(markdown_text: str) -> list[str]:
    lines = markdown_text.splitlines()
    blocks: list[str] = []
    collecting = False
    current: list[str] = []

    for line in lines:
        current.append(line)

    if collecting and current:
        block = "\n".join(current).strip()
        if block:
            blocks.append(block)

    return blocks


def make_chunker(method: str, chunk_size: int, overlap: int, sentences_per_chunk: int):
    if method == "FixedSizeChunker":
        return FixedSizeChunker(chunk_size=chunk_size, overlap=overlap)
    if method == "SentenceChunker":
        return SentenceChunker(max_sentences_per_chunk=sentences_per_chunk)
    return RecursiveChunker(chunk_size=chunk_size)


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.lower()))


def _safe_metric(value) -> float | None:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(numeric) or math.isinf(numeric):
        return None
    return numeric


def _fallback_answer_relevancy(question: str, answer: str) -> float:
    question_tokens = _tokenize(question)
    answer_tokens = _tokenize(answer)
    if not question_tokens or not answer_tokens:
        return 0.0
    overlap = len(question_tokens.intersection(answer_tokens))
    return overlap / len(question_tokens)


def _format_metric(value) -> str:
    numeric = _safe_metric(value)
    return f"{numeric:.3f}" if numeric is not None else "N/A"


def rank_chunks_by_query(chunks: list[str], query: str, top_k: int = 5) -> list[dict]:
    query = query.strip()
    if not query:
        return []

    query_tokens = _tokenize(query)
    ranked: list[dict] = []
    for idx, chunk in enumerate(chunks, start=1):
        chunk_tokens = _tokenize(chunk)
        overlap = len(query_tokens.intersection(chunk_tokens))
        if overlap == 0 and query.lower() not in chunk.lower():
            continue

        exact_bonus = 3 if query.lower() in chunk.lower() else 0
        score = overlap + exact_bonus
        ranked.append({"chunk_id": idx, "score": score, "content": chunk})

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked[:top_k]


@st.cache_data(show_spinner=False)
def load_eval_questions(path: Path) -> list[dict]:
    if not path.exists():
        return []

    content = path.read_text(encoding="utf-8")
    match = re.search(r"```jsonl\s*(.*?)\s*```", content, flags=re.DOTALL)
    if not match:
        return []

    rows: list[dict] = []
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def answer_with_gpt4o(query: str, contexts: list[str], model_name: str = DEFAULT_CHAT_MODEL) -> str:
    if not contexts:
        return "Không có context phù hợp để trả lời."

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Thiếu OPENAI_API_KEY. Hãy thêm key vào .env hoặc biến môi trường."

    try:
        from openai import OpenAI  # type: ignore[import-not-found]
    except Exception:
        return "Chưa cài package openai. Hãy chạy: pip install openai"

    client = OpenAI(api_key=api_key)
    context_text = "\n\n".join(f"[Context {idx}] {text}" for idx, text in enumerate(contexts, start=1))
    system_prompt = (
        "Bạn là trợ lý RAG. Trả lời ngắn gọn bằng tiếng Việt, chỉ dựa trên context được cung cấp. "
        "Nếu context không đủ thông tin, hãy nói rõ là chưa đủ dữ liệu."
    )
    user_prompt = (
        f"Câu hỏi: {query}\n\n"
        f"Context:\n{context_text}\n\n"
        "Hãy trả lời và nêu ngắn gọn context nào hỗ trợ câu trả lời."
    )

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content or "Không nhận được câu trả lời từ model."


def score_with_ragas(
    user_input: str,
    response: str,
    retrieved_contexts: list[str],
    reference: str,
) -> tuple[dict, str | None]:
    if not os.getenv("OPENAI_API_KEY"):
        return {}, "Thiếu OPENAI_API_KEY nên chưa thể chấm RAGAS."

    # Compatibility shim: some ragas versions still import this old module path.
    if "langchain_community.chat_models.vertexai" not in sys.modules:
        shim = types.ModuleType("langchain_community.chat_models.vertexai")

        class ChatVertexAI:  # pragma: no cover - compatibility fallback only
            def __init__(self, *args, **kwargs):
                raise RuntimeError("ChatVertexAI shim should not be instantiated in this demo.")

        shim.ChatVertexAI = ChatVertexAI
        sys.modules["langchain_community.chat_models.vertexai"] = shim

    try:
        from datasets import Dataset  # type: ignore[import-not-found]
        from ragas import evaluate  # type: ignore[import-not-found]
        from ragas.metrics import (  # type: ignore[import-not-found]
            answer_relevancy,
            context_precision,
            context_recall,
            faithfulness,
        )
    except Exception as exc:
        return {}, f"Thiếu package RAGAS/datasets hoặc import lỗi: {exc}"

    row = {
        "user_input": user_input,
        "response": response,
        "retrieved_contexts": retrieved_contexts,
        "reference": reference,
    }

    try:
        dataset = Dataset.from_list([row])
        result = evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        )
        scores = result.to_pandas().to_dict(orient="records")[0]
        if _safe_metric(scores.get("answer_relevancy")) is None:
            scores["answer_relevancy"] = _fallback_answer_relevancy(user_input, response)
            scores["answer_relevancy_note"] = "fallback_lexical_overlap"
        return scores, None
    except Exception as exc:
        return {}, f"Lỗi khi chạy RAGAS evaluate: {exc}"


def main() -> None:
    load_dotenv(override=False)
    st.set_page_config(page_title="Chunking Demo (Kenh14)", page_icon="🧩", layout="wide")
    st.title("🧩 Demo Chunking cho RAG (Kenh14 Star từ ngày 29/05/2026 đến 05/06/2026)")
    st.caption("Chọn 1 trong 3 phương pháp chunking và xem kết quả trực tiếp trên dữ liệu 1 tuần.")

    if not DATA_PATH.exists():
        st.error(f"Không tìm thấy dữ liệu: {DATA_PATH}")
        st.stop()

    markdown_text = load_markdown(DATA_PATH)
    noi_dung_blocks = extract_noi_dung_blocks(markdown_text)
    eval_questions = load_eval_questions(EVAL_PATH)

    with st.sidebar:
        st.header("Cấu hình")
        method = st.selectbox(
            "Phương pháp chunking",
            options=["FixedSizeChunker", "SentenceChunker", "RecursiveChunker"],
            index=0,
        )

        source_mode = st.radio(
            "Nguồn văn bản",
            options=["Toàn bộ file markdown"],
            index=0,
        )

        chunk_size = st.slider("chunk_size (ký tự)", min_value=100, max_value=2000, value=500, step=50)
        overlap = st.slider("overlap (chỉ cho FixedSize)", min_value=0, max_value=400, value=50, step=10)
        if overlap >= chunk_size:
            overlap = chunk_size - 1
        sentences_per_chunk = st.slider(
            "max_sentences_per_chunk (chỉ cho Sentence)",
            min_value=1,
            max_value=10,
            value=3,
            step=1,
        )

        run_llm = True
        llm_model = DEFAULT_CHAT_MODEL

    if source_mode == "Chỉ các mục ### Nội dung":
        selected_blocks = noi_dung_blocks[:len(noi_dung_blocks)]
        input_text = "\n\n".join(selected_blocks)
    else:
        input_text = markdown_text

    st.write(
        f"**Dataset:** `{DATA_PATH}` | "
        f"**Ký tự đầu vào:** {len(input_text):,}"
    )

    chunker = make_chunker(method, chunk_size, overlap, sentences_per_chunk)
    chunks = chunker.chunk(input_text)

    st.subheader("Query test (simple retrieval)")
    query_mode = st.radio(
        "Nguồn câu hỏi",
        options=["Nhập tay", "Chọn từ bộ câu hỏi RAGAS"],
        index=1 if eval_questions else 0,
    )

    selected_eval = None
    if query_mode == "Chọn từ bộ câu hỏi RAGAS" and eval_questions:
        options = {f"{item.get('id', '?')}: {item.get('user_input', '')}": item for item in eval_questions}
        selected_key = st.selectbox("Bộ câu hỏi benchmark", options=list(options.keys()))
        selected_eval = options[selected_key]
        query = selected_eval.get("user_input", "").strip()
    else:
        query = st.text_input("Nhập query", placeholder="Ví dụ: jang won young sân bay")

    top_k = st.slider("Top K kết quả query", min_value=1, max_value=20, value=5)

    if query.strip():
        ranked_results = rank_chunks_by_query(chunks, query, top_k=top_k)
        st.write(f"Tìm thấy **{len(ranked_results)}** chunk liên quan trong top-{top_k}.")
        if not ranked_results:
            st.info("Không có chunk nào khớp query theo cách match hiện tại.")
        for result in ranked_results:
            with st.expander(f"Chunk {result['chunk_id']} | score={result['score']}", expanded=False):
                st.text(result["content"])

        if run_llm:
            contexts = [item["content"] for item in ranked_results]
            with st.spinner("Đang gọi ChatGPT-4o..."):
                answer = answer_with_gpt4o(query=query, contexts=contexts, model_name=llm_model.strip() or DEFAULT_CHAT_MODEL)
            
            if query_mode == "Nhập tay":
                st.subheader("Câu trả lời từ ChatGPT-4o")
                st.write(answer)

            if selected_eval:
                st.subheader("Bảng so sánh kết quả")
                preview_contexts = contexts[:3]
                chatgpt_context_text = "\n\n".join(
                    f"- Context {idx}: {ctx[:300].replace(chr(10), ' ')}{'...' if len(ctx) > 300 else ''}"
                    for idx, ctx in enumerate(preview_contexts, start=1)
                )
                comparison_rows = [
                    {
                        "Title": "Câu hỏi",
                        "Mẫu (answer + context)": query,
                        "ChatGPT (answer + context)": query,
                    },
                    {
                        "Title": "Câu trả lời",
                        "Mẫu (answer + context)": selected_eval.get("reference", ""),
                        "ChatGPT (answer + context)": answer,
                    },
                    {
                        "Title": "Context",
                        "Mẫu (answer + context)": selected_eval.get("reference_context_hint", ""),
                        "ChatGPT (answer + context)": chatgpt_context_text or "Không có context retrieve được.",
                    },
                ]
                st.table(comparison_rows)

                st.subheader("RAGAS score")
                with st.spinner("Đang chấm điểm bằng RAGAS..."):
                    scores, error = score_with_ragas(
                        user_input=query,
                        response=answer,
                        retrieved_contexts=contexts,
                        reference=selected_eval.get("reference", ""),
                    )
                if error:
                    st.warning(error)
                else:
                    score_cols = st.columns(4)
                    score_cols[0].metric("faithfulness", _format_metric(scores.get("faithfulness")))
                    score_cols[1].metric("answer_relevancy", _format_metric(scores.get("answer_relevancy")))
                    score_cols[2].metric("context_precision", _format_metric(scores.get("context_precision")))
                    score_cols[3].metric("context_recall", _format_metric(scores.get("context_recall")))
                    if scores.get("answer_relevancy_note") == "fallback_lexical_overlap":
                        st.caption("answer_relevancy đang dùng fallback lexical-overlap vì RAGAS trả về NaN.")
                    st.json(scores)


if __name__ == "__main__":
    main()
