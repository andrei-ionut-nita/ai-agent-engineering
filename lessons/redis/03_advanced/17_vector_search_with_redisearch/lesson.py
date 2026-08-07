"""
Lesson 17: RediSearch vector indexes, KNN search over a toy embedding.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Redis is running first):

    docker compose up -d redis
    uv run python lessons/redis/03_advanced/17_vector_search_with_redisearch/lesson.py
"""

import os

import numpy as np
import redis
from dotenv import load_dotenv
from redis.commands.search.field import TextField, VectorField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query

load_dotenv()

# A deterministic bag-of-words vector over a fixed vocabulary, standing
# in for a real embedding model so this lesson needs no API key.
VOCAB = ["pizza", "dough", "bread", "sourdough", "garden", "tomato", "engine", "oil"]

NOTES = [
    "pizza dough rises overnight in the fridge before baking",
    "sourdough bread needs a starter and a long rise overnight",
    "tomato plants in the garden need staking as they grow",
    "the car engine oil should be changed every 5000 miles",
]

INDEX_NAME = "idx:notes"


def toy_embed(text: str) -> list[float]:
    words = text.lower().split()
    return [float(words.count(w)) for w in VOCAB]


def to_vector_bytes(values: list[float]) -> bytes:
    return np.array(values, dtype=np.float32).tobytes()


def create_index(r: redis.Redis) -> None:
    try:
        r.ft(INDEX_NAME).dropindex(delete_documents=True)
    except redis.ResponseError:
        pass  # no existing index, nothing to drop

    schema = (
        TextField("content"),
        VectorField(
            "embedding",
            "HNSW",
            {"TYPE": "FLOAT32", "DIM": len(VOCAB), "DISTANCE_METRIC": "COSINE"},
        ),
    )
    r.ft(INDEX_NAME).create_index(
        schema,
        definition=IndexDefinition(prefix=["note:"], index_type=IndexType.HASH),
    )


def main() -> None:
    dsn = os.environ["REDIS_DSN"]
    r = redis.Redis.from_url(dsn, decode_responses=False)

    create_index(r)

    for i, text in enumerate(NOTES):
        r.hset(
            f"note:{i}",
            mapping={"content": text, "embedding": to_vector_bytes(toy_embed(text))},
        )
    print(f"Indexed {len(NOTES)} notes")

    query_text = "bread that needs to rise"
    query_vector = to_vector_bytes(toy_embed(query_text))
    query = (
        Query("*=>[KNN 2 @embedding $vec AS score]")
        .return_fields("content", "score")
        .sort_by("score")  # KNN alone finds the k nearest, this orders them
        .dialect(2)
    )
    results = r.ft(INDEX_NAME).search(query, query_params={"vec": query_vector})

    print(f"Query: {query_text!r}")
    for i, doc in enumerate(results.docs, start=1):
        content = doc.content.decode() if isinstance(doc.content, bytes) else doc.content
        print(f"  {i}. {content} (score={doc.score})")


if __name__ == "__main__":
    main()
