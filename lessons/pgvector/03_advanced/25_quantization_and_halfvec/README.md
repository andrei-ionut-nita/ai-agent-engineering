# Lesson 25: `halfvec`, trading precision for half the storage

## Where we left off

Every `vector(N)` column in this course has stored full 32-bit floats
per dimension. `halfvec` stores 16-bit floats instead, half the
storage, half the memory an index needs to hold, and (as this lesson's
numbers show) barely any loss in ranking quality for typical embedding
data.

## What "half precision" actually means

A 32-bit float can represent numbers with far more precision than an
embedding actually needs, the direction a 768-number vector points
doesn't meaningfully change if the 6th decimal digit of one number
rounds differently. `halfvec` stores each dimension in 16 bits instead
of 32, this lesson's script confirms the on-disk difference directly
with `pg_column_size`.

## Declaring and using it

```sql
CREATE TABLE items (
    id bigserial PRIMARY KEY,
    embedding vector(768),
    embedding_half halfvec(768)
)
```

```python
from pgvector.utils import HalfVector

conn.execute(
    "INSERT INTO items (embedding, embedding_half) VALUES (%s, %s)",
    (Vector(vector), HalfVector(vector)),
)
```

`HalfVector`, from the same `pgvector` package as `Vector`, wraps a
Python list or NumPy array the same way, just adapted to `halfvec`
instead. The distance operators (`<=>`, `<->`, `<#>`) all work
identically on `halfvec` columns, and indexes use `halfvec_cosine_ops`,
`halfvec_l2_ops`, `halfvec_ip_ops` in place of the `vector_*_ops`
classes from Lessons 11-12.

## Why this matters beyond disk space

Smaller vectors mean an ANN index (Lessons 11-12) fits more of itself
in memory at once, and a memory-bound index is a faster index,
`halfvec` isn't just a storage optimization, it directly helps query
speed at scale. It also raises pgvector's indexable dimension ceiling:
`vector` indexes cap out at 2000 dimensions (why Lesson 4 truncated
Gemini's embeddings to 768), `halfvec` indexes go up to 4000, useful
for models with larger native output that you don't want to truncate
at all.

## The actual precision cost, measured

This lesson embeds the same 2,000 random vectors into both a `vector`
and a `halfvec` column, runs the identical top-5 nearest-neighbor query
against both, and compares the two result sets directly, expect them to
match exactly or nearly so. For most embedding-search use cases, this
is a genuinely close-to-free win; if your application is unusually
sensitive to tiny ranking differences (rare), benchmark on your own
real embeddings rather than assuming.

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/03_advanced/25_quantization_and_halfvec/lesson.py
```

## Checkpoint

- **`halfvec(N)`**: half-precision (16-bit) equivalent of `vector(N)`,
  roughly half the storage.
- **`HalfVector(...)`**: the `pgvector`-package wrapper, parallel to
  `Vector(...)`.
- **`halfvec_cosine_ops`** etc.: the index operator classes for
  `halfvec` columns, and a higher (4000) dimension cap for indexes.
- Ranking quality loss is typically negligible; benchmark your own data
  if in doubt.

If anything here still feels unclear, ask before moving to Lesson 26.
