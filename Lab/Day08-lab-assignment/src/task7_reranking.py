"""
Task 7 — Reranking Module.

- cross_encoder: OpenAI gpt-4o-mini chấm relevance query–document
- mmr: OpenAI embeddings + Maximal Marginal Relevance
- rrf: Reciprocal Rank Fusion (gộp nhiều ranked lists)
"""

import json
from copy import deepcopy

from src.rag_utils import LLM_MODEL, cosine_similarity, embed_query, embed_texts, get_openai_client


def rerank_cross_encoder(
    query: str, candidates: list[dict], top_k: int = 5
) -> list[dict]:
    """Rerank bằng OpenAI LLM scoring (0.0–1.0) cho từng candidate."""
    if not candidates:
        return []

    client = get_openai_client()
    docs_block = "\n\n".join(
        f"ID {i}:\n{c['content'][:1200]}"
        for i, c in enumerate(candidates)
    )

    response = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a relevance scorer for Vietnamese legal/news retrieval. "
                    "Return JSON: {\"scores\": [{\"id\": 0, \"score\": 0.95}, ...]} "
                    "where score is 0.0-1.0 for how well each document answers the query."
                ),
            },
            {
                "role": "user",
                "content": f"Query: {query}\n\nDocuments:\n{docs_block}",
            },
        ],
    )

    try:
        payload = json.loads(response.choices[0].message.content or "{}")
        score_map = {
            int(item["id"]): float(item["score"])
            for item in payload.get("scores", [])
        }
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        score_map = {i: c.get("score", 0.0) for i, c in enumerate(candidates)}

    reranked = []
    for i, candidate in enumerate(candidates):
        item = deepcopy(candidate)
        item["score"] = score_map.get(i, candidate.get("score", 0.0))
        reranked.append(item)

    reranked.sort(key=lambda x: x["score"], reverse=True)
    return reranked[:top_k]


def rerank_mmr(
    query_embedding: list[float],
    candidates: list[dict],
    top_k: int = 5,
    lambda_param: float = 0.7,
) -> list[dict]:
    """MMR với OpenAI embeddings — cân bằng relevance và diversity."""
    if not candidates:
        return []

    texts = [c["content"] for c in candidates]
    doc_embeddings = embed_texts(texts)

    selected: list[int] = []
    remaining = list(range(len(candidates)))

    for _ in range(min(top_k, len(candidates))):
        best_idx = None
        best_score = float("-inf")

        for idx in remaining:
            relevance = cosine_similarity(query_embedding, doc_embeddings[idx])
            max_sim = 0.0
            for sel_idx in selected:
                sim = cosine_similarity(doc_embeddings[idx], doc_embeddings[sel_idx])
                max_sim = max(max_sim, sim)
            mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim
            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = idx

        selected.append(best_idx)
        remaining.remove(best_idx)

    results = []
    for idx in selected:
        item = deepcopy(candidates[idx])
        relevance = cosine_similarity(query_embedding, doc_embeddings[idx])
        item["score"] = float(relevance)
        results.append(item)
    return results


def rerank_rrf(
    ranked_lists: list[list[dict]], top_k: int = 5, k: int = 60
) -> list[dict]:
    """Reciprocal Rank Fusion — gộp kết quả từ nhiều ranker."""
    rrf_scores: dict[str, float] = {}
    content_map: dict[str, dict] = {}

    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, start=1):
            key = item["content"]
            rrf_scores[key] = rrf_scores.get(key, 0.0) + 1.0 / (k + rank)
            content_map[key] = item

    sorted_items = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    results = []
    for content, score in sorted_items[:top_k]:
        merged = deepcopy(content_map[content])
        merged["score"] = score
        results.append(merged)
    return results


def rerank(
    query: str,
    candidates: list[dict],
    top_k: int = 5,
    method: str = "cross_encoder",
) -> list[dict]:
    """Unified reranking interface."""
    if method == "cross_encoder":
        return rerank_cross_encoder(query, candidates, top_k)
    if method == "mmr":
        query_embedding = embed_query(query)
        return rerank_mmr(query_embedding, candidates, top_k)
    if method == "rrf":
        return rerank_rrf([candidates], top_k=top_k)
    raise ValueError(f"Unknown rerank method: {method}")


if __name__ == "__main__":
    dummy_candidates = [
        {"content": "Điều 248: Tội tàng trữ trái phép chất ma tuý", "score": 0.8, "metadata": {}},
        {"content": "Nghệ sĩ X bị bắt vì sử dụng ma tuý", "score": 0.7, "metadata": {}},
        {"content": "Hình phạt tù từ 2-7 năm cho tội tàng trữ", "score": 0.6, "metadata": {}},
    ]
    results = rerank("hình phạt tàng trữ ma tuý", dummy_candidates, top_k=2)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content']}")
