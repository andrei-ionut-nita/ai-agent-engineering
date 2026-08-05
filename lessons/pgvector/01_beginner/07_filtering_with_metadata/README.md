# Lesson 7: Combining a `WHERE` filter with vector search

## Where we left off

Every search so far has looked across *all* stored chunks. This lesson
adds an ordinary column, `category`, and narrows the search to a subset
before ranking by distance, something `InMemoryVectorStore` has no
natural way to do at all, since it has no query language of its own.

## Metadata is just another column

```sql
CREATE TABLE notes (
    id bigserial PRIMARY KEY,
    content text NOT NULL,
    category text NOT NULL,
    embedding vector(768)
)
```

There's nothing pgvector-specific about `category`, it's a plain `text`
column, stored in the same row as the embedding. This is the payoff of
"a vector column inside a normal table" from Lesson 1: filtering by
metadata is just `WHERE`, the same as it would be for any other query.

## Filter first, then rank by distance

```sql
SELECT content, embedding <=> %s AS distance
FROM notes
WHERE category = %s
ORDER BY distance
LIMIT %s
```

Postgres narrows the rows to only the matching `category` first, *then*
computes and sorts by distance only among those. This is exactly the
kind of query a real application needs constantly: "find the closest
matches, but only from this user's documents," "only from documents
tagged `public`," "only from the last 30 days." Every one of those is
one extra `WHERE` clause, not a different kind of search.

## Why this is awkward without a database

To do the equivalent with `InMemoryVectorStore`, you'd filter the
Python list of documents yourself before searching, or search
everything and discard results after the fact, both are less efficient
and more code than one `WHERE` clause, and get worse as the filtering
logic grows (multiple tags, date ranges, permission checks).

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/01_beginner/07_filtering_with_metadata/lesson.py
```

## Checkpoint

- Metadata alongside a `vector` column is just an ordinary column,
  filtered with ordinary `WHERE`.
- `WHERE ... ORDER BY <distance> LIMIT k` narrows the candidate rows
  first, then ranks only among those.
- This combination has no clean equivalent in a plain in-memory vector
  store, it falls out for free from being real SQL.

If anything here still feels unclear, ask before moving to Lesson 8.
