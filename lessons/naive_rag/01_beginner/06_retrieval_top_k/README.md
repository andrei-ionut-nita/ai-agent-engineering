# Lesson 6: Retrieval, Top-k

## What we're building

A function that takes a question, embeds it, compares it against every
chunk in the vector store from Lesson 5, and returns the `k` most
similar ones. This is the "retrieve" stage, the third of Naive RAG's
four stages, and the first time the question itself gets embedded.

## The question is embedded too

Every lesson so far embedded document text. Retrieval embeds the
*question* the exact same way, using the exact same embedding model,
into the exact same 768-number space as every chunk. That's what makes
comparison possible at all: cosine similarity (Lesson 3) only means
something when both vectors came from the same embedding model, into
the same space.

Note there's no keyword overlap required. "What's the best way to get a
crispy pizza crust?" doesn't share a single distinctive word with "the
best pizza dough recipe... baking at the highest oven setting, with a
preheated steel," yet embedding-based retrieval finds that chunk anyway,
because it's comparing *meaning*, not matching words. A keyword search
(the pre-embedding way of doing this) would need "crispy," "crust,"
"pizza," or similar words to actually appear in the text to find it at
all.

## The code, piece by piece

```python
query_vector = embed_texts([query])[0]
```

Reuses Lesson 5's batch `embed_texts` even for a single query, wrapping
it in a one-item list and taking the first (only) result back out,
rather than writing a separate single-item embedding function.

```python
scored = [
    {**record, "score": cosine_similarity(query_vector, record["embedding"])}
    for record in store
]
```

For every record in the store, compute how similar its embedding is to
the query's embedding, and build a new dict that has everything the
original record had (`**record` unpacks it) plus a new `"score"` key.
This is a **linear scan**: checking every single record, one at a time,
no shortcuts. It's fine at 5 records; Lesson 19 comes back to why it
stops being fine at scale.

```python
scored.sort(key=lambda record: record["score"], reverse=True)
return scored[:k]
```

Sort the scored records from highest similarity to lowest, then slice
off just the first `k`. This is exactly what "top-k retrieval" means:
the `k` best matches, nothing more.

## Running it

```bash
uv run python lessons/naive_rag/01_beginner/06_retrieval_top_k/lesson.py
```

## Expected output

```
Query: "What's the best way to get a crispy pizza crust?"

Top 2 chunks:

  1. (score=0.7xxx) The best pizza dough recipe found so far uses 00 flour, a 48-hour cold...
  2. (score=0.5xxx) <some other chunk, a distant second>
```

The exact scores vary slightly between runs (Gemini's embeddings aren't
perfectly deterministic), but the pizza recipe chunk should consistently
win by a clear margin, despite no shared distinctive vocabulary with the
question.

## Checkpoint

- **retrieval**: embed the question, compare it to every chunk's
  embedding, return the most similar ones.
- **linear scan**: checking every record one by one, the simplest
  possible search strategy, and the one this lesson uses.
- **top-k**: keeping only the `k` highest-scoring results, discarding
  the rest.
- Retrieval finds chunks by meaning, not by shared words, the entire
  advantage embeddings have over a plain keyword search.

If anything here still feels unclear, ask before moving to Lesson 7.
