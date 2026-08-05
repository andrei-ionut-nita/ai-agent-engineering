# Lesson 9: Beginner Checkpoint - Notes Semantic Search CLI

## What this is

No new concepts in this lesson. This is a checkpoint: a small, real
script built entirely out of ideas from Lessons 1 through 8, combined
into one thing. If you can read `lesson.py` and understand why every
piece is there, you've mastered the Beginner tier. If any piece feels
unfamiliar, that's a sign to revisit the lesson it came from before
continuing to Intermediate.

## What it does

Loads the same `notes.txt` used throughout this tier, embeds and stores
it in Postgres with a `category` tag per chunk, then runs a handful of
example searches: a plain semantic search, a category-filtered search,
and a search after one note has been edited and re-embedded, printing
each result set so you can see the whole lifecycle in one run.

## Where each piece came from

```python
conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
register_vector(conn)
```
Lesson 1 (enabling the extension) and Lesson 3 (`register_vector`,
teaching the connection to translate Python lists to and from
`vector`).

```python
CREATE TABLE notes (
    id bigserial PRIMARY KEY,
    content text NOT NULL,
    category text NOT NULL,
    embedding vector(768)
)
```
Lesson 3 (the `vector(N)` column type) and Lesson 7 (a plain metadata
column living alongside it).

```python
embeddings_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    output_dimensionality=EMBEDDING_DIMENSIONS,
)
vectors = embeddings_model.embed_documents(chunks)
```
Lesson 4 (`output_dimensionality`, `embed_documents`, storing real
embeddings instead of toy ones).

```python
cur.executemany(
    "INSERT INTO notes (content, category, embedding) VALUES (%s, %s, %s)",
    [...],
)
```
Lesson 2 (parameterized queries, never f-string SQL) and Lesson 4
(`executemany` for bulk inserts).

```python
"SELECT content, embedding <=> %s AS distance FROM notes ORDER BY distance LIMIT %s"
```
Lesson 5 (`<=>`, the cosine distance operator, the one Gemini's
embeddings are meant to be compared with) and Lesson 6 (`ORDER BY
... LIMIT k` as the whole top-k search).

```python
"... WHERE category = %s ORDER BY distance LIMIT %s"
```
Lesson 7 (narrowing to a category before ranking by distance).

```python
conn.execute("UPDATE notes SET content = %s, embedding = %s WHERE id = %s", ...)
```
Lesson 8 (always re-embedding together with any content edit).

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/01_beginner/09_beginner_checkpoint_project/lesson.py
```

You should see: a plain search correctly finding the pizza dough chunk
for a question about bread (no keyword overlap, same trick as langchain
Lesson 28), a category-filtered search finding the best match *within*
`garden` even though it isn't the closest match overall, and a search
result changing after a note is edited and re-embedded.

## Try this yourself

Without looking anything up:

- Add a new chunk of your own (a made-up note about a topic not already
  covered) with its own `category`, does it show up correctly when you
  search for something related?
- Change the query used for the category-filtered search to something
  about recipes instead of gardening, does it correctly still return
  nothing useful from `category='garden'`?
- Delete a note with `DELETE FROM notes WHERE id = ...` and confirm a
  search that used to return it no longer does.

If you can make these changes confidently, you're ready for the
Intermediate tier, starting at Lesson 10.
