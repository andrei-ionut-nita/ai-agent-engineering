# Lesson 5: An In-Memory Vector Store

## What we're building

A function that chunks a document (Lesson 4), embeds every chunk
(Lesson 2), and holds the results in one Python list. That list is this
lesson's **vector store**, deliberately the simplest possible one:
nothing gets saved to disk, and there's no library involved beyond the
embedding call itself.

## A vector store is simpler than the name suggests

"Vector store" and "vector database" sound like specialized
infrastructure, and at scale, they are (this repo's `pgvector` course
covers a real one). But at its core, a vector store is just a collection
of records, each one pairing a piece of text with its embedding:

```python
[{"text": chunk, "embedding": vector}, ...]
```

That's genuinely it. Everything a real vector database adds on top
(persisting to disk, indexing for fast search over millions of records,
metadata filtering) is optimization layered on top of this same idea,
not a fundamentally different one. Building the plain-list version first
means Lesson 20's jump to `chromadb` later in this course will feel like
a natural next step, not a black box.

## The code, piece by piece

```python
response = client.models.embed_content(
    model=EMBEDDING_MODEL,
    contents=texts,
    ...
)
```

Lesson 2 passed a single string wrapped in a one-item list to `contents`.
Here, `texts` is already a list of every chunk, embedded in **one**
network call instead of one call per chunk. This matters for two
reasons: it's faster (one round trip instead of five), and it uses up
far less of the free tier's requests-per-minute quota, which counts
*calls*, not chunks. From here on, this course always embeds in batches
like this wherever more than one piece of text needs embedding.

```python
return [{"text": chunk, "embedding": vector} for chunk, vector in zip(chunks, vectors)]
```

`zip` pairs up the original `chunks` list with the `vectors` list the
embedding call returned, position by position (the first chunk with the
first vector, and so on, since `embed_content` preserves input order).
The result is the list-of-dicts vector store described above.

## Running it

```bash
uv run python lessons/naive_rag/01_beginner/05_an_in_memory_vector_store/lesson.py
```

## Expected output

```
Vector store built: 5 records

  Record 1: embedding of length 768 for: The bookshelf in the study is organized by color, not by author or gen...
  Record 2: embedding of length 768 for: Currently learning Bach's Cello Suite No. 1, focusing on the Prelude m...
  Record 3: embedding of length 768 for: The garden at the back of the house has three raised beds. The first b...
  Record 4: embedding of length 768 for: The best pizza dough recipe found so far uses 00 flour, a 48-hour cold...
  Record 5: embedding of length 768 for: Project Aurora is a personal weather station built from a Raspberry Pi...
```

If you see a `429 RESOURCE_EXHAUSTED` error, the free tier's embedding
quota is briefly used up (batching into one call, as this lesson does,
minimizes this, but it can still happen while you're running lessons
back to back testing things out). Wait a minute and rerun, see the
[Troubleshooting section](../../../../README.md#troubleshooting) in
this project's root README.

## Checkpoint

- **vector store**: a collection of `{text, embedding}` records, nothing
  more at its core, no matter how much infrastructure sits on top of
  that idea in a real system.
- **batch embedding**: passing every chunk to `embed_content` in one
  call (`contents=texts`) instead of one call per chunk, faster and much
  friendlier to rate limits.
- This in-memory list is what Lesson 6 searches over, and what Lesson 20
  eventually replaces with `chromadb`.

If anything here still feels unclear, ask before moving to Lesson 6.
