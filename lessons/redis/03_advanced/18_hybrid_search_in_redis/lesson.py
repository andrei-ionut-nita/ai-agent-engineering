"""
Lesson 18: hybrid search, a TagField filter combined with vector KNN.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Redis is running first):

    docker compose up -d redis
    uv run python lessons/redis/03_advanced/18_hybrid_search_in_redis/lesson.py
"""

import os

import numpy as np
import redis
from dotenv import load_dotenv
from redis.commands.search.field import TagField, TextField, VectorField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query

load_dotenv()

VOCAB = ["pizza", "dough", "bread", "sourdough", "garden", "tomato", "engine", "oil"]

NOTES = [
    ("pizza dough rises overnight in the fridge", "cooking"),
    ("sourdough bread needs a starter and a long rise", "cooking"),
    ("tomato plants in the garden need staking", "gardening"),
    ("car engine oil should be changed every 5000 miles", "automotive"),
]

INDEX_NAME = "idx:hybrid_notes"


def toy_embed(text: str) -> list[float]:
    words = text.lower().split()
    return [float(words.count(w)) for w in VOCAB]


def to_vector_bytes(values: list[float]) -> bytes:
    return np.array(values, dtype=np.float32).tobytes()


def create_index(r: redis.Redis) -> None:
    try:
        r.ft(INDEX_NAME).dropindex(delete_documents=True)
    except redis.ResponseError:
        pass

    schema = (
        TextField("content"),
        TagField("category"),
        VectorField(
            "embedding",
            "HNSW",
            {"TYPE": "FLOAT32", "DIM": len(VOCAB), "DISTANCE_METRIC": "COSINE"},
        ),
    )
    r.ft(INDEX_NAME).create_index(
        schema,
        definition=IndexDefinition(prefix=["hnote:"], index_type=IndexType.HASH),
    )


def main() -> None:
    dsn = os.environ["REDIS_DSN"]
    r = redis.Redis.from_url(dsn, decode_responses=False)

    create_index(r)

    for i, (text, category) in enumerate(NOTES):
        r.hset(
            f"hnote:{i}",
            mapping={
                "content": text,
                "category": category,
                "embedding": to_vector_bytes(toy_embed(text)),
            },
        )
    categories = ", ".join(category for _, category in NOTES)
    print(f"Indexed {len(NOTES)} notes across categories: {categories}")

    query_text = "bread that needs to rise"
    query_vector = to_vector_bytes(toy_embed(query_text))
    query = (
        Query("@category:{cooking}=>[KNN 2 @embedding $vec AS score]")
        .return_fields("content", "category", "score")
        .sort_by("score")
        .dialect(2)
    )
    results = r.ft(INDEX_NAME).search(query, query_params={"vec": query_vector})

    print(f"Hybrid query: category=cooking, vector~{query_text!r}")
    for i, doc in enumerate(results.docs, start=1):
        content = doc.content.decode() if isinstance(doc.content, bytes) else doc.content
        category = doc.category.decode() if isinstance(doc.category, bytes) else doc.category
        print(f"  {i}. {content} ({category}, score={doc.score})")


if __name__ == "__main__":
    main()
