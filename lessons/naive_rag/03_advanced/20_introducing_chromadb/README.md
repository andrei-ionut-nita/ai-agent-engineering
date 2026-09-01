# Lesson 20: Introducing chromadb

## Where we left off

Lesson 19 measured the actual cost of a linear scan at scale. This
lesson introduces the fix: `chromadb`, a real, open-source vector
database, still entirely local (no server, no account, no API key
beyond Gemini's), that indexes vectors instead of scanning every one of
them on every query.

## What changes, and what doesn't

The four-stage shape (chunk, embed, retrieve, generate) doesn't change
at all. What changes is *where the vectors live and how they're
searched*: a Python list you scan yourself, versus a database that
indexes them and answers "most similar" queries without checking every
record one by one. This lesson only replaces the storage and retrieval
half, nothing about chunking or generation is any different from
Lesson 15.

## The code, piece by piece

```python
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="notes")
```

`chromadb.Client()` with no arguments creates an **ephemeral, in-memory**
database, everything it stores disappears when the program exits, the
database equivalent of this course's own Python list, just with real
indexing underneath. A `collection` is chromadb's name for what this
course has been calling a "vector store," a named group of records.

```python
collection.add(
    ids=[path.stem for path in paths],
    documents=texts,
    embeddings=vectors,
    metadatas=[{"source": path.name} for path in paths],
)
```

Unlike this course's list-of-dicts (one dict per record, each with its
own `text`/`embedding`/`source` keys), chromadb wants four *parallel*
lists, matched up by position: unique `ids`, the `documents` (raw text),
the `embeddings` (vectors this course already computed with
`embed_texts`, chromadb doesn't compute its own), and `metadatas` (one
dict of extra fields per record, same idea as Lesson 12's `source`
field).

```python
results = collection.query(query_embeddings=[query_vector], n_results=2)
```

The retrieval half of Lesson 6's `retrieve()`, expressed as a method
call instead of a manual sort: pass a query embedding (still computed
with this course's own `embed_texts`, chromadb never sees the raw query
text here), get back the `n_results` closest matches, already ranked.

## Running it

```bash
uv run python lessons/naive_rag/03_advanced/20_introducing_chromadb/lesson.py
```

## Expected output

```
Query: "What's the best way to get a crispy pizza crust?"

Collection has 5 documents

Top 2 results from chromadb:
  pizza-dough: distance=0.2167
  garden: distance=0.3456
```

The same two documents Lesson 6's hand-rolled cosine similarity found,
in the same order, chromadb's index arrives at the identical answer, it
just does it with indexing structures built for this at scale, instead
of comparing against every record one at a time. Note `distance` here is
smaller-is-more-similar (chromadb defaults to a squared-L2-style
distance), the opposite direction from this course's own cosine
*similarity* scores, where bigger meant more similar, worth noticing so
the two don't get read backwards later.

## Checkpoint

- **chromadb.Client()**: an ephemeral, in-memory vector database, the
  same role this course's own Python list has played, with a real index
  underneath instead of a linear scan.
- **collection.add()**: parallel lists (`ids`, `documents`, `embeddings`,
  `metadatas`), matched by position, chromadb's version of this course's
  list of `{text, embedding, source}` dicts.
- **collection.query()**: chromadb's version of `retrieve()`, already
  ranked, no manual sort needed.
- chromadb's `distance` is smaller-is-better, the opposite direction
  from this course's own cosine *similarity*, which was bigger-is-better.

If anything here still feels unclear, ask before moving to Lesson 21.
