# Lesson 28: Advanced Capstone - A FastAPI RAG Service on pgvector

## What this is

No new pgvector concepts in this lesson. This is the capstone: every
idea from this entire course, wired into one small, realistically
shaped web service. If you can read `lesson.py` and understand why
every piece is there, you've completed this course. If any piece feels
unfamiliar, that's a sign to revisit the lesson it came from.

## What it does

A FastAPI app, `NotesRAGService`, exposing three endpoints:

- `POST /notes`: upsert one or more notes (insert-or-update, embedding
  and indexing them).
- `GET /search?q=...&k=...`: hybrid search (vector + full-text, fused
  by rank).
- `POST /ask`: a full RAG answer, retrieve relevant notes, ask the
  model to answer using only that context.

The script builds the app, then exercises it end to end using
FastAPI's `TestClient` (so running this lesson produces deterministic,
printed output, the same convention as every other lesson in this
course, rather than requiring you to leave a server running and poke
it from another terminal). A real deployment would instead run:

```bash
uvicorn lesson:app --reload
```

## Where each piece came from

```python
pool = ConnectionPool(conninfo=dsn, min_size=2, max_size=10, configure=register_vector)
```
Lesson 18 (pooling) and Lesson 19 (registering `vector` on every
pooled connection via `configure`).

```python
CREATE TABLE notes (
    external_id text PRIMARY KEY,
    content text NOT NULL,
    category text NOT NULL,
    embedding vector(768),
    content_tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
)
CREATE INDEX ON notes USING hnsw (embedding vector_cosine_ops)
```
Lesson 7 (metadata column), Lesson 12 (HNSW), Lesson 16 (the generated
`tsvector` column for full-text search).

```python
INSERT INTO notes (...) VALUES (...)
ON CONFLICT (external_id) DO UPDATE SET ...
```
Lesson 15 (upsert) combined with Lesson 8's rule: any content change
re-embeds in the same statement.

```python
fused = reciprocal_rank_fusion(vector_ranking, text_ranking)
```
Lesson 16 (running both kinds of search) and Lesson 17 (fusing them by
rank).

```python
retriever = vector_store.as_retriever(search_kwargs={"k": 2})
chain = {"context": ..., "question": ...} | prompt | model | StrOutputParser()
```
Lesson 20 (`PGVector`, the langchain-compatible store) and Lesson 21
(the full RAG chain built on top of it).

```python
@app.post("/notes")
async def upsert_notes(notes: list[NoteIn]) -> dict: ...
```
New in this lesson only in the sense of *shape*: FastAPI's request/response
models (`pydantic`, familiar if you've used it elsewhere) and route
decorators are how everything above gets exposed over HTTP, the actual
logic inside each route is entirely Lessons 1-27.

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/03_advanced/28_advanced_capstone_project/lesson.py
```

You should see: notes ingested via `POST /notes`, a hybrid search via
`GET /search` returning a fused ranking, and a RAG answer via
`POST /ask` that correctly says it doesn't know about baking bread
(only pizza dough is in the notes), the same honest-about-its-context
behavior from Lesson 21, now reachable over HTTP.

## Try this yourself

Without looking anything up:

- Run `uvicorn lesson:app --reload` from this folder instead, and hit
  `GET /search?q=yeast` from your browser or `curl`, confirm it behaves
  identically to the `TestClient` calls in the script.
- Add a `category` query parameter to `/search`, filtering hybrid
  search to one category (Lesson 7, plus everything here).
- Add a `DELETE /notes/{external_id}` endpoint (Lesson 8's `DELETE`
  lifecycle, exposed over HTTP).

If you can make these changes confidently, you've completed the
pgvector course. From here, langchain Lessons 27-29 and this course's
Lessons 20-21 are worth re-reading together, you now know both what
`InMemoryVectorStore` was hiding, and what actually replaces it.
