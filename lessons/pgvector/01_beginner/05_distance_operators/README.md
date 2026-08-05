# Lesson 5: The three distance operators, `<->`, `<#>`, `<=>`

## Where we left off

Lesson 4 got real embeddings into a table. This lesson measures how far
apart two of them are, which is the entire mechanism behind "search by
meaning": find the stored vectors *closest* to a query vector.

## Three ways to measure "closest"

pgvector adds three operators, each a different definition of distance
between two vectors:

| Operator | Name | Smaller means |
|---|---|---|
| `<->` | L2 (Euclidean) distance | straight-line distance between the two points |
| `<#>` | negative inner product | more similar (it's negated so "smaller is closer" still holds) |
| `<=>` | cosine distance | more similar in *direction*, ignoring vector length |

```sql
SELECT embedding <-> %s AS l2_distance FROM notes WHERE id = 1;
SELECT embedding <#> %s AS neg_inner_product FROM notes WHERE id = 1;
SELECT embedding <=> %s AS cosine_distance FROM notes WHERE id = 1;
```

All three take a stored vector on the left and a query vector on the
right (or vice versa, the operators are symmetric), and return a single
number.

## Why three, and which to use

Gemini's embeddings (like most modern embedding models) are trained so
that **cosine distance** is the intended similarity measure, meaning is
carried by the *direction* the vector points, not by how long it is.
`<=>` is what this course uses for every real search from here on.
`<->` (L2) is the more general-purpose "distance in space" measure used
in other domains (like plain coordinates); `<#>` (inner product) is
fastest to compute but only meaningful when vectors are pre-normalized
to the same length, Lesson 13 comes back to exactly this tradeoff.

## Seeing it directly

```python
query_vector = embeddings_model.embed_query("recipes and cooking")
row = conn.execute(
    "SELECT content, embedding <=> %s AS distance FROM notes ORDER BY distance LIMIT 1",
    (Vector(query_vector),),
).fetchone()
```

Notice this is the same shape of query used to explore in Lesson 3,
just with the query vector as a parameter instead of comparing two
stored rows.

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/01_beginner/05_distance_operators/lesson.py
```

## Checkpoint

- **`<->`**: L2 (Euclidean) distance.
- **`<#>`**: negative inner product (negated so smaller still means
  closer).
- **`<=>`**: cosine distance, the one Gemini's embeddings are meant to
  be compared with, and what this course uses going forward.

If anything here still feels unclear, ask before moving to Lesson 6.
