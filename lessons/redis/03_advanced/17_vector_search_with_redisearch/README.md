# Lesson 17: `RediSearch` vector indexes, Redis as a vector store

## Where we left off

Lesson 9 cached by an exact prompt hash, honest that it couldn't match
prompts that mean the same thing but aren't worded identically. This
lesson closes that gap the real way: a vector index, the same idea
pgvector's course built on Postgres (`<=>`, `ORDER BY ... LIMIT k`),
built here on Redis instead, via the `search` module confirmed loaded
back in Lesson 2.

## A toy embedding, so no API key is needed

Every other lesson in this course avoids calling a real model. This
one still needs *some* numeric vector to index, so it uses a small,
deterministic bag-of-words vector over a fixed vocabulary instead of a
real embedding model:

```python
VOCAB = ["pizza", "dough", "bread", "sourdough", "garden", "tomato", "engine", "oil"]

def toy_embed(text: str) -> list[float]:
    words = text.lower().split()
    return [float(words.count(w)) for w in VOCAB]
```

It's crude (no real understanding of meaning, just word overlap over
eight fixed words) but it's *directionally* correct for this lesson's
purpose: two sentences about bread end up numerically closer to each
other than either is to a sentence about car engines. A real system
swaps this one function for `GoogleGenerativeAIEmbeddings`, exactly
what pgvector's Lesson 4 does, everything downstream (the index, the
query) is unchanged.

## Defining the index

```python
from redis.commands.search.field import VectorField, TextField
from redis.commands.search.index_definition import IndexDefinition, IndexType

schema = (
    TextField("content"),
    VectorField("embedding", "HNSW", {
        "TYPE": "FLOAT32",
        "DIM": len(VOCAB),
        "DISTANCE_METRIC": "COSINE",
    }),
)
r.ft("idx:notes").create_index(
    schema,
    definition=IndexDefinition(prefix=["note:"], index_type=IndexType.HASH),
)
```

`FT.CREATE` (here, `create_index`) is `CREATE INDEX ... USING hnsw` from
pgvector Lesson 12, same algorithm, same idea, different database.
`prefix=["note:"]` tells the index which keys to include automatically,
any hash whose key starts with `note:` and has an `embedding` field is
indexed the moment it's written, no separate "add to index" step.

## Storing a vector

```python
import numpy as np

vector_bytes = np.array(toy_embed(text), dtype=np.float32).tobytes()
r.hset(f"note:{note_id}", mapping={"content": text, "embedding": vector_bytes})
```

`RediSearch` expects a vector field as raw bytes in the type declared
in the schema (`FLOAT32` here), `numpy`'s `.tobytes()` produces exactly
that. This mirrors pgvector's `register_vector`, translating a Python
list into the format the database's vector type expects.

## Querying: `KNN`, RediSearch's `ORDER BY <=> LIMIT k`

```python
from redis.commands.search.query import Query

query_vector = np.array(toy_embed("bread that needs to rise"), dtype=np.float32).tobytes()
q = (
    Query("*=>[KNN 2 @embedding $vec AS score]")
    .return_fields("content", "score")
    .sort_by("score")
    .dialect(2)
)
results = r.ft("idx:notes").search(q, query_params={"vec": query_vector})
```

`*=>[KNN k @field $param AS score]` reads oddly at first but does
exactly what `ORDER BY embedding <=> %s LIMIT k` did in pgvector: `*`
means "consider every indexed document", `KNN k` narrows the candidate
set to the `k` nearest by the field's configured distance metric, `AS
score` names the resulting distance so it can be read back per result.
`KNN` alone only picks *which* `k` documents come back, not what order
they arrive in, `.sort_by("score")` is the explicit `ORDER BY` on top,
skip it and the results come back in an arbitrary order even though
they're the right `k`. `.dialect(2)` opts into the query syntax
version that supports parameterized vector queries; RediSearch has
kept older dialects around for backward compatibility, this course
always uses `2`.

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/03_advanced/17_vector_search_with_redisearch/lesson.py
```

## Expected output

```
Indexed 4 notes
Query: 'bread that needs to rise'
  1. sourdough bread needs a starter and a long rise overnight (score=0.29...)
  2. pizza dough rises overnight in the fridge before baking (score=1.0)
```

(the two bread-related notes rank ahead of the tomato and engine
notes, exact `score` values depend on floating point rounding, that's
fine)

## Checkpoint

- **`FT.CREATE` with a `VectorField`**: `HNSW`, a distance metric, and
  a dimension, the RediSearch equivalent of pgvector's `CREATE INDEX
  ... USING hnsw`.
- **`prefix=[...]`**: keys matching the prefix are indexed
  automatically on write, no separate "add to index" call.
- **`KNN k @field $param AS score`** plus **`.sort_by("score")`**: the
  query-time equivalent of `ORDER BY <=> LIMIT k`, `KNN` alone only
  picks the `k`, sorting by the named score orders them.

If anything here still feels unclear, ask before moving to Lesson 18.
