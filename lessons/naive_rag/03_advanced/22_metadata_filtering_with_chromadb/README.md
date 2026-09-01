# Lesson 22: Metadata Filtering with chromadb

## Where we left off

Lesson 12 filtered this course's own Python list by a `source` field
before ranking by similarity. This lesson does the identical thing on a
chromadb backend, using its built-in `where` clause instead of a list
comprehension.

## The code, piece by piece

```python
metadatas=[{"source": path.name, "area": area} for path, area in zip(paths, areas)]
```

A second metadata field, `area`, alongside the `source` field from
Lesson 20-21. Nothing about chromadb requires exactly one metadata
field, any dict of extra values works, this lesson just needs a second
one to filter by.

```python
filtered = collection.query(
    query_embeddings=[query_vector],
    n_results=1,
    where={"area": "study"},
)
```

`where={"area": "study"}` narrows the candidate pool to only records
whose `area` metadata equals `"study"`, *before* ranking by similarity,
same ordering of operations as Lesson 12's Python-level filter. This is
the chromadb-native way of expressing the exact same idea, a query
scoped to a subset of the collection instead of the whole thing.

## Running it

```bash
uv run python lessons/naive_rag/03_advanced/22_metadata_filtering_with_chromadb/lesson.py
```

## Expected output

```
Unfiltered top match: ['pizza-dough']
Filtered to area='study': ['<one of bookshelf, cello-practice, or weather-station>']
```

Same pattern as Lesson 12's `cello-practice.md` example: forcing the
search into the wrong scope (`pizza-dough` isn't tagged `area='study'`)
still returns a confident top-1 result, just not a useful one. A
metadata filter changes *which* records are eligible, it doesn't make
the eventual match any more relevant to the question.

## Checkpoint

- **`where` clause**: chromadb's built-in way to narrow a query by
  metadata before ranking, the same idea as Lesson 12's Python-level
  filter, expressed natively.
- A real vector database's metadata filtering is typically far faster
  than filtering a Python list by hand at scale, since it can use its
  own indexes on metadata fields too, not just on the vectors.
- Filtering to the wrong scope is still a real failure mode here, same
  as Lesson 12, a database doesn't fix a badly-scoped query, it just
  executes it faster.

If anything here still feels unclear, ask before moving to Lesson 23.
