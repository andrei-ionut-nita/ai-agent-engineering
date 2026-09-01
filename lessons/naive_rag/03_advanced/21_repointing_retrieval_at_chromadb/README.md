# Lesson 21: Repointing Retrieval at chromadb

## Where we left off

Lesson 20 introduced `chromadb`'s API in isolation, one script, one
query, side by side with what this course's own `retrieve()` would have
returned. This lesson does the real swap: `ask()`, unchanged in shape
since Lesson 8, now runs entirely on a chromadb backend instead of a
Python list.

## The interface stays the same, the implementation doesn't

```python
def ask(query: str, collection: chromadb.Collection, k: int = 2) -> str:
    retrieved = retrieve(query, collection, k)
    return generate_answer(query, retrieved)
```

Compare this to Lesson 8's `ask()`. The signature is different (`store:
list[dict]` became `collection: chromadb.Collection`), but the shape,
retrieve then generate, is identical. This is exactly the point of
building the hand-rolled version first: everything downstream of
retrieval (prompting, generation, this course's whole mental model of
what RAG *is*) never had to change when the storage backend did.

## The code, piece by piece

```python
def retrieve(query: str, collection: chromadb.Collection, k: int) -> list[str]:
    query_vector = embed_texts([query])[0]
    results = collection.query(query_embeddings=[query_vector], n_results=k)
    documents = results["documents"]
    assert documents is not None
    return documents[0]
```

Embedding the query is unchanged, still this course's own `embed_texts`.
What's different is everything after that: instead of scoring every
record by hand and sorting, `collection.query()` does it, and returns
the matching documents directly (`results["documents"][0]`, the `[0]`
because chromadb supports querying with multiple query vectors at once,
this lesson always passes exactly one).

## Running it

```bash
uv run python lessons/naive_rag/03_advanced/21_repointing_retrieval_at_chromadb/lesson.py
```

## Expected output

```
Q: What's the best way to get a crispy pizza crust?
A: <a grounded answer about 00 flour, cold ferment, preheated steel, identical in substance to Lesson 7's answer>
```

The answer should read essentially the same as Lesson 7's version of
this exact question, same retrieval result, same prompt shape, same
model, only the storage and search mechanics underneath changed.

## Checkpoint

- Swapping a storage backend (list to chromadb) didn't require changing
  `generate_answer()`, `ask()`'s signature shape, or the prompt at all,
  only what's inside `retrieve()`.
- This is what "the interface stays the same" buys you in practice: a
  bigger architectural change (a real vector database instead of a
  list) stayed contained to one function.

If anything here still feels unclear, ask before moving to Lesson 22.
