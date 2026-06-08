"""
Task 6 — Lexical Search Module (BM25).
"""

from rank_bm25 import BM25Okapi

from src.rag_utils import COLLECTION_NAME, get_weaviate_client
from src.task4_chunking_indexing import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    load_documents,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

CORPUS: list[dict] = []
_BM25: BM25Okapi | None = None


def _tokenize(text: str) -> list[str]:
    return text.lower().split()


def _fetch_corpus_from_weaviate() -> list[dict]:
    client = get_weaviate_client()
    try:
        if not client.collections.exists(COLLECTION_NAME):
            return []

        collection = client.collections.get(COLLECTION_NAME)
        corpus = []
        for obj in collection.iterator():
            corpus.append({
                "content": obj.properties.get("content", ""),
                "metadata": {
                    "source": obj.properties.get("source", ""),
                    "type": obj.properties.get("doc_type", ""),
                    "chunk_index": obj.properties.get("chunk_index", 0),
                },
            })
        return corpus
    finally:
        client.close()


def _build_corpus_from_markdown() -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    corpus = []
    for doc in load_documents():
        for i, text in enumerate(splitter.split_text(doc["content"])):
            corpus.append({
                "content": text,
                "metadata": {**doc["metadata"], "chunk_index": i},
            })
    return corpus


def build_bm25_index(corpus: list[dict]) -> BM25Okapi:
    global CORPUS, _BM25
    CORPUS = corpus
    tokenized = [_tokenize(doc["content"]) for doc in corpus]
    _BM25 = BM25Okapi(tokenized)
    return _BM25


def _ensure_index():
    global _BM25
    if _BM25 is not None:
        return

    corpus = _fetch_corpus_from_weaviate()
    if not corpus:
        corpus = _build_corpus_from_markdown()
    if not corpus:
        build_bm25_index([])
        return
    build_bm25_index(corpus)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm từ khóa sử dụng BM25.

    Returns:
        List of {'content': str, 'score': float, 'metadata': dict}, sorted descending.
    """
    _ensure_index()
    if not CORPUS or _BM25 is None:
        return []

    tokenized_query = _tokenize(query)
    if not tokenized_query:
        return []

    scores = _BM25.get_scores(tokenized_query)
    ranked_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True,
    )

    results = []
    for idx in ranked_indices[:top_k]:
        score = float(scores[idx])
        if score <= 0:
            continue
        results.append({
            "content": CORPUS[idx]["content"],
            "score": score,
            "metadata": CORPUS[idx]["metadata"],
        })
    return results


if __name__ == "__main__":
    results = lexical_search("Điều 248 tàng trữ trái phép chất ma tuý", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")
