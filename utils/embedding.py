"""Qwen Embedding API wrapper for knowledge base vector search."""
import os
import math
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = OpenAI(
    api_key=os.getenv("QWEN_API_KEY"),
    base_url=os.getenv("QWEN_BASE_URL"),
)

# Qwen embedding dimension (text-embedding-v4 outputs 1024-dim vectors)
EMBEDDING_DIM = 1024


def generate_embedding(text: str) -> list[float]:
    """Convert text to an embedding vector via Qwen Embedding API."""
    response = _client.embeddings.create(
        model="text-embedding-v4",
        input=text,
    )
    return response.data[0].embedding


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
