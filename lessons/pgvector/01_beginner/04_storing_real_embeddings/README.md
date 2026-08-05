# Lesson 4: Storing real embeddings, not toy 3-number vectors

## Where we left off

Lesson 3 stored a made-up 3-number vector, just to see the mechanics.
This lesson replaces that with the real thing: Gemini's embedding
model, the exact one langchain Lesson 28 used for `InMemoryVectorStore`.

## One new setting: `output_dimensionality`

```python
embeddings_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    output_dimensionality=768,
)
```

Left at its default, `gemini-embedding-001` produces 3072 numbers per
embedding. That matters here for a very concrete reason: pgvector's
indexes (the ones built in Lessons 11-12) cap out at 2000 dimensions for
the plain `vector` type, and 3072 is over that cap. `output_dimensionality`
asks the model to produce a shorter vector directly (768 is a common
choice, still large enough to capture meaning well), so every later
lesson that indexes these embeddings can actually build one. Set this
once, and use the same value everywhere in this course, mixing
dimensions between rows in the same column isn't possible anyway,
`vector(N)` enforces one exact `N`.

## Embedding many chunks at once

```python
vectors = embeddings_model.embed_documents(chunks)
```

`embed_documents` takes a list of strings and returns a list of
embeddings, one per string, more efficient than calling `embed_query`
in a loop when you already have everything to embed up front.

## Storing content and embedding together

```python
with conn.cursor() as cur:
    cur.executemany(
        "INSERT INTO notes (content, embedding) VALUES (%s, %s)",
        [(chunk, Vector(vector)) for chunk, vector in zip(chunks, vectors)],
    )
```

`executemany` runs the same statement once per tuple in the list,
here inserting every chunk alongside its embedding in one call instead
of a manual Python loop calling `execute` repeatedly. Each row now holds
both the original text (so you can show it back to a user) and its
vector (so you can search by meaning), the two live together in the
same table.

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/01_beginner/04_storing_real_embeddings/lesson.py
```

This reuses the same `notes.txt` from langchain Lessons 27-28, split
into the same six chunks, so you can compare directly: same data, now
embedded into Postgres instead of an in-memory Python object.

## Checkpoint

- **`output_dimensionality`**: asks the embedding model to produce a
  shorter vector directly, needed here to stay under pgvector's
  2000-dimension index limit.
- **`embed_documents`**: embeds a list of strings at once, one vector
  per string.
- **`executemany`**: runs one parameterized statement once per row,
  inserting content and its embedding together.

If anything here still feels unclear, ask before moving to Lesson 5.
