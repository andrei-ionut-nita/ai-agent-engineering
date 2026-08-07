# Lesson 18: Combining vector similarity with filters/full-text in one query

## Where we left off

Lesson 17's query considered every indexed document. A real search
usually also needs to narrow by something exact first, a category, an
owner, a status, before ranking what's left by similarity. RediSearch
does both in one query, the same idea as pgvector Lesson 16's hybrid
search, just phrased in RediSearch's own query syntax instead of SQL.

## Adding a filterable field to the schema

```python
from redis.commands.search.field import TagField

schema = (
    TextField("content"),
    TagField("category"),
    VectorField("embedding", "HNSW", {...}),
)
```

`TagField` is for exact-match filtering (a category, a status, a tenant
ID), distinct from `TextField`, which is for full-text search (word
matching, stemming, relevance scoring on prose). This lesson filters on
a `TagField`; combining a `TextField` search with a vector query
follows the same pattern, a text clause instead of a tag clause before
the `=>`.

## The hybrid query

```python
q = (
    Query("@category:{cooking}=>[KNN 2 @embedding $vec AS score]")
    .return_fields("content", "category", "score")
    .sort_by("score")
    .dialect(2)
)
```

`@category:{cooking}` is a tag filter, exact match against the
`category` field, curly braces are RediSearch's tag-value syntax. The
`=>[KNN ...]` clause after it means "of the documents that pass this
filter, find the k nearest by vector distance", filter first, rank
second, in one round trip to Redis, not a vector search followed by a
separate Python-side filter over the results.

## Why filter-then-rank, not rank-then-filter

If the query instead ran an unfiltered `KNN` and threw away results
that didn't match `category` afterward, asking for `KNN 2` could
return zero results in the target category, if the two nearest
vectors overall both happened to be `gardening` notes. Filtering
first, inside the same query, guarantees the `k` nearest are chosen
*from the already-narrowed set*, the same ordering guarantee pgvector
Lesson 16's `WHERE ... AND embedding <=> ...` gives.

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/03_advanced/18_hybrid_search_in_redis/lesson.py
```

## Expected output

```
Indexed 4 notes across categories: cooking, cooking, gardening, automotive
Hybrid query: category=cooking, vector~'bread that needs to rise'
  1. sourdough bread needs a starter and a long rise (cooking, score=0.29...)
  2. pizza dough rises overnight in the fridge (cooking, score=1.0)
```

(both results are `cooking`, even though nothing in the query text
says "cooking", the tag filter did that, ranking is purely from the
vector)

## Checkpoint

- **`TagField`**: exact-match filtering, distinct from `TextField`'s
  full-text search.
- **`@field:{value}=>[KNN ...]`**: filter first, rank the filtered set
  by vector distance second, one query, one round trip.
- **why order matters**: filtering after a `KNN` can return fewer than
  `k` results in the target category, filtering inside the query
  can't.

If anything here still feels unclear, ask before moving to Lesson 19.
