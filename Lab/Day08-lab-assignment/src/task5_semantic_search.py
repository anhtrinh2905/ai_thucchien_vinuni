"""
Task 5 — Semantic Search Module (dense retrieval on Weaviate + OpenAI embeddings).
"""

from weaviate.classes.query import MetadataQuery

from src.rag_utils import COLLECTION_NAME, embed_query, get_weaviate_client


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm ngữ nghĩa sử dụng vector similarity trên Weaviate.

    Returns:
        List of {'content': str, 'score': float, 'metadata': dict}, sorted descending.
    """
    if not query.strip():
        return []

    query_vector = embed_query(query)
    client = get_weaviate_client()

    try:
        if not client.collections.exists(COLLECTION_NAME):
            return []

        collection = client.collections.get(COLLECTION_NAME)
        response = collection.query.near_vector(
            near_vector=query_vector,
            limit=top_k,
            return_metadata=MetadataQuery(distance=True),
        )

        results = []
        for obj in response.objects:
            distance = obj.metadata.distance if obj.metadata else 1.0
            score = max(0.0, 1.0 - float(distance))
            results.append({
                "content": obj.properties.get("content", ""),
                "score": score,
                "metadata": {
                    "source": obj.properties.get("source", ""),
                    "type": obj.properties.get("doc_type", ""),
                    "chunk_index": obj.properties.get("chunk_index", 0),
                },
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    finally:
        client.close()


if __name__ == "__main__":
    results = semantic_search("hình phạt cho tội tàng trữ ma tuý", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")
