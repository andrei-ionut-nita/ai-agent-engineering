# Lesson 19: Intermediate Checkpoint - Hybrid Search API

## What this is

No new concepts in this lesson. This is a checkpoint: a small, real
service class built entirely out of ideas from Lessons 10 through 18,
combined into one thing. If you can read `lesson.py` and understand why
every piece is there, you've mastered the Intermediate tier. If any
piece feels unfamiliar, that's a sign to revisit the lesson it came
from before continuing to Advanced.

## What it does

A `NotesSearchService` class wrapping a connection pool: `upsert_notes`
ingests documents (insert-or-update by `external_id`, embedding and
indexing them), and `search` runs both a vector search and a full-text
search, then merges them with reciprocal rank fusion. The script builds
the service, ingests `notes.txt`'s six chunks, re-ingests one of them
with edited content (proving the upsert path re-embeds correctly), and
runs a hybrid search.

## Where each piece came from

```python
self.pool = ConnectionPool(conninfo=dsn, min_size=2, max_size=10, configure=register_vector)
self.pool.wait()
```
Lesson 18 (a small set of reused connections, not one per call) and
Lesson 3 (`register_vector`, here passed as the pool's `configure`
callback so every connection the pool opens gets it, not just the
first). One new wrinkle worth noticing: the extension has to be created
on a plain bootstrap connection *before* the pool opens anything,
`register_vector` needs to look up the `vector` type, which only exists
once `CREATE EXTENSION` has already run.

```python
CREATE TABLE notes (
    external_id text PRIMARY KEY,
    content text NOT NULL,
    category text NOT NULL,
    embedding vector(768),
    content_tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
)
```
Lesson 7 (metadata column), Lesson 16 (the generated `tsvector` column
for full-text search).

```python
CREATE INDEX ON notes USING hnsw (embedding vector_cosine_ops)
```
Lesson 12 (HNSW, built after data is loaded).

```python
INSERT INTO notes (external_id, content, category, embedding)
VALUES (%s, %s, %s, %s)
ON CONFLICT (external_id) DO UPDATE
SET content = EXCLUDED.content, category = EXCLUDED.category, embedding = EXCLUDED.embedding
```
Lesson 15 (upsert, so re-running ingestion updates existing rows
instead of erroring or duplicating) combined with Lesson 8's rule (any
content change re-embeds in the same statement).

```python
vector_ranking = [...]   # ORDER BY embedding <=> %s
text_ranking = [...]     # ORDER BY ts_rank(...) DESC
fused = reciprocal_rank_fusion(vector_ranking, text_ranking)
```
Lesson 16 (running both kinds of search) and Lesson 17 (fusing them by
rank instead of by raw, differently-scaled scores).

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/02_intermediate/19_intermediate_checkpoint_project/lesson.py
```

You should see: six notes ingested and indexed, one of them
re-ingested with different content and correctly re-embedded (the
Lesson 8 lifecycle, now via upsert instead of a manual `UPDATE`), and a
hybrid search whose fused ranking reflects both keyword and semantic
signal.

## Try this yourself

Without looking anything up:

- Add a `category` filter parameter to `search`, so it's possible to
  hybrid-search within only one category (Lesson 7 plus everything
  here).
- Change `k` in reciprocal rank fusion from 60 to something much
  smaller (like 1) and see how much more the fused ranking gets
  dominated by whichever result was rank 1 in either list.
- Add a second `NotesSearchService` instance pointed at the same
  database and confirm both can search concurrently through their own
  pools without interfering with each other.

If you can make these changes confidently, you're ready for the
Advanced tier, starting at Lesson 20.
