# Lesson 27: What breaks when you upgrade your embedding model

## Where we left off

Lesson 8 warned about one kind of drift: editing text without
re-embedding it. This lesson covers a subtler, easy-to-miss version of
the same problem: changing *how* you embed, a new model, a new
`output_dimensionality`, even a different `task_type` setting, and what
happens to everything already stored.

## The trap: same dimension, same column, silently incompatible vectors

```python
old_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001", output_dimensionality=768, task_type="RETRIEVAL_DOCUMENT"
)
new_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001", output_dimensionality=768, task_type="SEMANTIC_SIMILARITY"
)
```

Both configurations produce a 768-number vector for the exact same
text. Postgres has no way to notice anything changed, `vector(768)`
accepts either one without complaint. But embed the *same sentence*
under both settings and compare them directly: this lesson measures a
cosine similarity of roughly 0.82 between them, not 1.0. They describe
meaningfully different points in meaningfully different spaces. Store
half your rows under the old configuration and half under the new one
in the same column, and every search from then on is comparing vectors
that were never meant to be compared, with no error, no warning,
just steadily worse results.

## The same trap applies to swapping models entirely, or dimensions

Anything that changes *how* an embedding is produced, a new model
version, a different `output_dimensionality` truncation, a different
`task_type`, a different provider, invalidates every vector stored
under the old configuration. This includes situations that look
harmless: bumping a model version string, a config change that seems
unrelated to search quality.

## The migration pattern: a versioned column, backfilled, then swapped

```sql
ALTER TABLE notes ADD COLUMN embedding_v2 vector(768);
```

1. Add the new embedding as a *new* column, don't overwrite the old one
   in place.
2. Backfill: re-embed every existing row's `content` with the new
   configuration, writing into `embedding_v2`, while `embedding` (the
   old column) keeps serving live searches, unaffected, undisturbed.
3. Verify: confirm `embedding_v2` is populated for every row, and
   spot-check that searches against it return sensible results.
4. Cut over: point application queries at `embedding_v2` (or rename
   columns), only once step 3 is confirmed.
5. Drop the old column, once nothing depends on it anymore.

This is the same shape as any zero-downtime schema migration, additive
first, backfilled, verified, only then cut over, applied to the fact
that an embedding is itself a kind of schema that can go stale.

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/03_advanced/27_migrations_and_reembedding_drift/lesson.py
```

## Checkpoint

- Two vectors from different embedding configurations can share a
  dimension and still describe meaningfully different spaces, verified
  here at roughly 0.82 cosine similarity for the identical text.
- Nothing in Postgres or pgvector detects this, it must be handled at
  the application/migration level.
- **Migration pattern**: add a new column, backfill by re-embedding,
  verify, cut over, drop the old column, never overwrite embeddings
  from a different configuration in place.

If anything here still feels unclear, ask before moving to Lesson 28.
