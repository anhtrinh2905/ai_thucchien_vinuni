"""
Task 8 — PageIndex Vectorless RAG (+ OpenAI fallback khi chưa có PageIndex API).
"""

import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv

from src.rag_utils import cosine_similarity, embed_query, embed_texts

load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
DOC_IDS_CACHE = Path(__file__).parent.parent / "data" / ".pageindex_doc_ids.json"
POLL_INTERVAL_SEC = 2
MAX_POLL_ATTEMPTS = 30


def _pageindex_configured() -> bool:
    return bool(PAGEINDEX_API_KEY and "xxx" not in PAGEINDEX_API_KEY)


def _load_doc_ids() -> dict[str, str]:
    if DOC_IDS_CACHE.exists():
        return json.loads(DOC_IDS_CACHE.read_text(encoding="utf-8"))
    return {}


def _save_doc_ids(mapping: dict[str, str]):
    DOC_IDS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    DOC_IDS_CACHE.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")


def upload_documents():
    """Upload markdown documents lên PageIndex (convert sang .md path upload via temp if needed)."""
    if not _pageindex_configured():
        raise RuntimeError("PAGEINDEX_API_KEY chưa được cấu hình trong .env")

    from pageindex import PageIndexClient

    client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
    mapping = _load_doc_ids()

    for md_file in sorted(STANDARDIZED_DIR.rglob("*.md")):
        key = str(md_file.relative_to(STANDARDIZED_DIR))
        if key in mapping:
            print(f"  ✓ Already uploaded: {key}")
            continue

        result = client.submit_document(file_path=str(md_file))
        doc_id = result.get("doc_id")
        if not doc_id:
            raise RuntimeError(f"Upload failed for {md_file.name}: {result}")
        mapping[key] = doc_id
        print(f"  ✓ Uploaded: {key} → {doc_id}")

    _save_doc_ids(mapping)
    return mapping


def _wait_for_retrieval(client, retrieval_id: str) -> dict:
    for _ in range(MAX_POLL_ATTEMPTS):
        result = client.get_retrieval(retrieval_id)
        status = result.get("status", "")
        if status in ("completed", "success", "ready"):
            return result
        if status in ("failed", "error"):
            raise RuntimeError(f"PageIndex retrieval failed: {result}")
        time.sleep(POLL_INTERVAL_SEC)
    raise TimeoutError(f"PageIndex retrieval timeout: {retrieval_id}")


def _search_pageindex_api(query: str, top_k: int) -> list[dict]:
    from pageindex import PageIndexClient

    client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
    doc_ids = _load_doc_ids()
    if not doc_ids:
        doc_ids = upload_documents()

    results = []
    for path, doc_id in doc_ids.items():
        if not client.is_retrieval_ready(doc_id):
            continue
        submitted = client.submit_query(doc_id=doc_id, query=query)
        retrieval_id = submitted.get("retrieval_id")
        if not retrieval_id:
            continue
        payload = _wait_for_retrieval(client, retrieval_id)
        chunks = payload.get("results") or payload.get("chunks") or payload.get("retrieval_results") or []
        if isinstance(chunks, dict):
            chunks = chunks.get("items", [])
        for i, chunk in enumerate(chunks):
            if isinstance(chunk, str):
                content = chunk
                score = 1.0 - i * 0.05
                metadata = {"source": Path(path).name, "type": Path(path).parts[0]}
            else:
                content = chunk.get("text") or chunk.get("content") or str(chunk)
                score = float(chunk.get("score", 1.0 - i * 0.05))
                metadata = chunk.get("metadata") or {"source": Path(path).name}
            results.append({
                "content": content,
                "score": score,
                "metadata": metadata,
                "source": "pageindex",
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def _search_openai_fallback(query: str, top_k: int) -> list[dict]:
    """Fallback vectorless: OpenAI embeddings chọn đoạn liên quan từ markdown."""
    from src.task4_chunking_indexing import load_documents

    paragraphs: list[dict] = []
    for doc in load_documents():
        for block in doc["content"].split("\n\n"):
            text = block.strip()
            if len(text) < 80:
                continue
            paragraphs.append({
                "content": text[:2000],
                "metadata": doc["metadata"],
            })

    if not paragraphs:
        return []

    # Giới hạn số đoạn để embed nhanh trong test/demo
    paragraphs = paragraphs[:120]
    vectors = embed_texts([p["content"] for p in paragraphs])
    query_vec = embed_query(query)

    scored = []
    for para, vec in zip(paragraphs, vectors):
        scored.append({
            "content": para["content"],
            "score": cosine_similarity(query_vec, vec),
            "metadata": para["metadata"],
            "source": "pageindex",
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Vectorless retrieval using PageIndex (hoặc OpenAI fallback).
    """
    if not query.strip():
        return []

    if _pageindex_configured():
        try:
            return _search_pageindex_api(query, top_k)
        except Exception:
            pass

    return _search_openai_fallback(query, top_k)


if __name__ == "__main__":
    if not _pageindex_configured():
        print("⚠ PAGEINDEX_API_KEY chưa cấu hình — dùng OpenAI fallback")
    results = pageindex_search("hình phạt sử dụng ma tuý", top_k=3)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")
