"""Shared utilities for RAG tasks 5–10."""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536
LLM_MODEL = "gpt-4o-mini"
COLLECTION_NAME = "DrugLawDocs"


def get_openai_client() -> OpenAI:
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def embed_query(query: str) -> list[float]:
    client = get_openai_client()
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query,
        dimensions=EMBEDDING_DIM,
    )
    return response.data[0].embedding


def embed_texts(texts: list[str]) -> list[list[float]]:
    client = get_openai_client()
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
        dimensions=EMBEDDING_DIM,
    )
    return [item.embedding for item in response.data]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def get_weaviate_client():
    from src.task4_chunking_indexing import get_weaviate_client as _get_client

    return _get_client()
