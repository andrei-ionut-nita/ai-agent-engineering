# Lesson 6: `ORDER BY ... LIMIT k`, the whole search in one query

## Where we left off

Lesson 5 measured distance to exactly one row (`LIMIT 1`, implicitly,
by taking `.fetchone()`). This lesson makes it a real top-k search:
the closest *k* rows to a query, ranked, in one statement.

## The whole thing is one SQL pattern

```sql
SELECT content, embedding <=> %s AS distance
FROM notes
ORDER BY distance
LIMIT %s
```

This is the entire mechanism `vector_store.similarity_search(query,
k=2)` was doing for you in langchain Lesson 28, just spelled out:
compute a distance column for every row, `ORDER BY` it ascending
(closest first), `LIMIT` to the top *k*. Ordinary SQL, nothing new
syntactically, just a column that happens to be a vector distance.

## Why this scales in a way Python sorting doesn't

`InMemoryVectorStore.similarity_search` computes distance to every
stored vector in a Python loop, then sorts the results, entirely in
your program's memory. This query does the same conceptual work, but
Postgres is a database built to sort and limit large sets efficiently,
and (starting in Lesson 11) can use an index to avoid checking every row
at all. The SQL doesn't change between "6 rows" and "6 million rows";
what changes is whether an index exists, covered in the next tier.

## `k`, chosen at query time

```python
def search(conn, query_vector, k):
    return conn.execute(
        "SELECT content, embedding <=> %s AS distance FROM notes ORDER BY distance LIMIT %s",
        (query_vector, k),
    ).fetchall()
```

`k` is just a parameter, decided per call, not baked into the table or
the query's structure. Ask for `k=1` when you want the single best
match, `k=5` when you want several candidates to feed to something
else, exactly the role `k` played in langchain's `similarity_search`.

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/01_beginner/06_similarity_search_basics/lesson.py
```

## Checkpoint

- **top-k vector search**: `ORDER BY <distance column> LIMIT k`, one
  SQL query, no different in shape from ordering by any other column.
- This is what `similarity_search` was doing under the hood, in Python,
  over an in-memory list; here it's the database doing it.
- `k` is an ordinary query parameter, chosen per call.

If anything here still feels unclear, ask before moving to Lesson 7.
