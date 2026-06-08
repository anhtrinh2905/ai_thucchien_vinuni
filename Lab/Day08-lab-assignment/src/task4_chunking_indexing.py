"""
Task 4 — Chunking & Indexing vào Vector Store.

Cài đặt:
    pip install langchain-text-splitters langchain-experimental langchain-openai openai weaviate-client python-dotenv
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"

# =============================================================================
# CONFIGURATION
# =============================================================================

# SemanticChunker: tách theo độ tương đồng ngữ nghĩa giữa các câu (embedding),
# giúp mỗi chunk giữ trọn một ý/điều luật thay vì cắt cứng theo ký tự.
CHUNK_SIZE = 1000
# Giới hạn tối đa mỗi chunk khi post-split; tránh chunk quá dài làm loãng retrieval.

CHUNK_OVERLAP = 50
# Overlap khi post-split các semantic chunk vượt CHUNK_SIZE.

CHUNKING_METHOD = "semantic"

# Percentile càng cao → ít điểm cắt hơn → chunk lớn hơn (85 cân bằng legal + news).
SEMANTIC_BREAKPOINT_PERCENTILE = 85

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536

VECTOR_STORE = "weaviate"
COLLECTION_NAME = "DrugLawDocs"

_EMBED_BATCH_SIZE = 100


def _is_weaviate_cloud() -> bool:
    url = os.getenv("WEAVIATE_URL", "")
    api_key = os.getenv("WEAVIATE_API_KEY", "")
    return bool(url and api_key and "xxx" not in url and "xxx" not in api_key)


def _vector_index_config():
    """Weaviate Cloud chỉ hỗ trợ hfresh; local Docker dùng hnsw."""
    from weaviate.classes.config import Configure, VectorDistances

    if _is_weaviate_cloud():
        return Configure.VectorIndex.hfresh(
            distance_metric=VectorDistances.COSINE,
        )
    return Configure.VectorIndex.hnsw(
        distance_metric=VectorDistances.COSINE,
    )


def get_weaviate_client():
    """Kết nối Weaviate Cloud nếu có credentials, ngược lại dùng local Docker."""
    import weaviate
    from weaviate.auth import AuthApiKey

    url = os.getenv("WEAVIATE_URL", "")
    api_key = os.getenv("WEAVIATE_API_KEY", "")

    if url and api_key and "xxx" not in url and "xxx" not in api_key:
        return weaviate.connect_to_weaviate_cloud(
            cluster_url=url,
            auth_credentials=AuthApiKey(api_key),
        )
    return weaviate.connect_to_local()


def load_documents() -> list[dict]:
    """
    Đọc toàn bộ markdown files từ data/standardized/.

    Returns:
        List of {'content': str, 'metadata': {'source': str, 'type': str}}
    """
    documents = []
    for md_file in sorted(STANDARDIZED_DIR.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        doc_type = "legal" if "legal" in md_file.parts else "news"
        documents.append({
            "content": content,
            "metadata": {
                "source": md_file.name,
                "type": doc_type,
                "path": str(md_file.relative_to(STANDARDIZED_DIR)),
            },
        })
    return documents


def _get_semantic_splitter():
    from langchain_experimental.text_splitter import SemanticChunker
    from langchain_openai import OpenAIEmbeddings

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        dimensions=EMBEDDING_DIM,
    )
    return SemanticChunker(
        embeddings=embeddings,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=SEMANTIC_BREAKPOINT_PERCENTILE,
    )


def _enforce_chunk_size(texts: list[str]) -> list[str]:
    """Post-split các semantic chunk quá dài để không vượt CHUNK_SIZE."""
    max_allowed = int(CHUNK_SIZE * 1.1)
    oversized = [t for t in texts if len(t) > max_allowed]
    if not oversized:
        return texts

    size_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    result: list[str] = []
    for text in texts:
        if len(text) <= max_allowed:
            result.append(text)
        else:
            result.extend(size_splitter.split_text(text))
    return result


def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    Chunk documents bằng SemanticChunker, post-split nếu vượt CHUNK_SIZE.

    Returns:
        List of {'content': str, 'metadata': dict} — mỗi item là 1 chunk
    """
    semantic_splitter = _get_semantic_splitter()
    chunks: list[dict] = []

    for doc in documents:
        semantic_splits = semantic_splitter.split_text(doc["content"])
        sized_splits = _enforce_chunk_size(semantic_splits)

        for i, text in enumerate(sized_splits):
            chunks.append({
                "content": text,
                "metadata": {
                    **doc["metadata"],
                    "chunk_index": i,
                },
            })

    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """
    Embed toàn bộ chunks bằng OpenAI text-embedding-3-small.

    Returns:
        Mỗi chunk dict được thêm key 'embedding': list[float]
    """
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    texts = [c["content"] for c in chunks]

    for start in range(0, len(texts), _EMBED_BATCH_SIZE):
        batch = texts[start : start + _EMBED_BATCH_SIZE]
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch,
            dimensions=EMBEDDING_DIM,
        )
        for j, item in enumerate(response.data):
            chunks[start + j]["embedding"] = item.embedding

    return chunks


def index_to_vectorstore(chunks: list[dict]):
    """Lưu chunks vào Weaviate."""
    from weaviate.classes.config import Configure, DataType, Property

    client = get_weaviate_client()
    index_type = "hfresh" if _is_weaviate_cloud() else "hnsw"
    print(f"  Weaviate vector index: {index_type}")

    try:
        if client.collections.exists(COLLECTION_NAME):
            client.collections.delete(COLLECTION_NAME)

        collection = client.collections.create(
            name=COLLECTION_NAME,
            vector_config=Configure.Vectors.self_provided(
                vector_index_config=_vector_index_config(),
            ),
            properties=[
                Property(name="content", data_type=DataType.TEXT),
                Property(name="source", data_type=DataType.TEXT),
                Property(name="doc_type", data_type=DataType.TEXT),
                Property(name="chunk_index", data_type=DataType.INT),
            ],
        )

        with collection.batch.dynamic() as batch:
            for chunk in chunks:
                meta = chunk["metadata"]
                batch.add_object(
                    properties={
                        "content": chunk["content"],
                        "source": meta.get("source", ""),
                        "doc_type": meta.get("type", ""),
                        "chunk_index": meta.get("chunk_index", 0),
                    },
                    vector=chunk["embedding"],
                )

        failed = collection.batch.failed_objects
        if failed:
            raise RuntimeError(f"Weaviate batch insert failed: {len(failed)} objects")
    finally:
        client.close()


def run_pipeline():
    """Chạy toàn bộ pipeline: load → chunk → embed → index."""
    print("=" * 50)
    print("Task 4: Chunking & Indexing")
    print(f"  Chunking: {CHUNKING_METHOD} (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}, percentile={SEMANTIC_BREAKPOINT_PERCENTILE})")
    print(f"  Embedding: {EMBEDDING_MODEL} (dim={EMBEDDING_DIM})")
    print(f"  Vector Store: {VECTOR_STORE}")
    print("=" * 50)

    docs = load_documents()
    print(f"\n✓ Loaded {len(docs)} documents")

    chunks = chunk_documents(docs)
    print(f"✓ Created {len(chunks)} chunks")

    chunks = embed_chunks(chunks)
    print(f"✓ Embedded {len(chunks)} chunks")

    index_to_vectorstore(chunks)
    print("✓ Indexed to vector store")


if __name__ == "__main__":
    run_pipeline()
