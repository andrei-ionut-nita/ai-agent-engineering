# Lesson 20: `langchain-postgres`'s `PGVector`, replacing `InMemoryVectorStore`

## Where we left off

This is the moment this whole course has been building toward. langchain
Lesson 28 built an `InMemoryVectorStore` and said outright it wasn't
meant for production. Lessons 1-19 here built the same capability by
hand, on Postgres. This lesson closes the loop: swap in
`langchain-postgres`'s `PGVector`, a class that speaks the exact same
`VectorStore` interface as `InMemoryVectorStore`, backed by everything
this course just built.

## The swap, almost line for line

langchain Lesson 28:
```python
from langchain_core.vectorstores import InMemoryVectorStore

vector_store = InMemoryVectorStore(embeddings_model)
vector_store.add_documents(chunks)
```

Here:
```python
from langchain_postgres import PGVector

vector_store = PGVector(
    embeddings=embeddings_model,
    connection=postgres_dsn,
    collection_name="notes",
)
vector_store.add_documents(chunks)
```

Same `embeddings_model` (Gemini). Same `add_documents`. Same
`similarity_search(query, k=2)` afterward, `PGVector` implements
langchain's `VectorStore` interface, so any code written against
`InMemoryVectorStore` (Lesson 29's `@tool`-wrapped search included)
keeps working completely unchanged, only the constructor call and the
import line differ.

## What `PGVector` is actually doing underneath

Everything from this course, wired up for you: it creates its own
tables (using SQLAlchemy internally, one for the "collection," one for
the embedded documents themselves), stores each document's embedding in
a `vector` column, and translates `similarity_search` into the
`ORDER BY embedding <=> ... LIMIT k` query pattern from Lesson 6. The
`collection_name` groups multiple logical document sets in the same
database, this course's `notes` collection could live alongside another
project's `product_descriptions` collection, in the same Postgres
instance, without interfering.

## Why reach for this instead of the hand-rolled version

Lessons 1-19 taught the underlying mechanism deliberately, so none of
this is a black box. In an actual application, `PGVector` is usually the
better default: it already handles metadata filtering, connection
management, and schema creation, tested and maintained as part of
LangChain's own ecosystem, letting you skip re-implementing it. Reach
for the raw `psycopg` approach when you need something `PGVector`
doesn't expose (custom indexing strategy, hybrid search exactly like
Lesson 16, tight control over the schema), otherwise this is the
practical choice.

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/03_advanced/20_langchain_pgvector_integration/lesson.py
```

This re-runs langchain Lesson 28's exact query, "What do I know about
baking bread at home?", against `PGVector` instead of
`InMemoryVectorStore`, same data, same result, now backed by Postgres.

## Checkpoint

- **`PGVector`**: `langchain-postgres`'s Postgres-backed `VectorStore`,
  a drop-in replacement for `InMemoryVectorStore`.
- Same interface (`add_documents`, `similarity_search`) means existing
  langchain code (tools, chains) needs no changes beyond the
  constructor.
- **`collection_name`**: groups multiple logical document sets in one
  database.

If anything here still feels unclear, ask before moving to Lesson 21.
