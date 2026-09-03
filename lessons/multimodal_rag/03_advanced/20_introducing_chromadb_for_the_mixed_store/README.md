# Lesson 20: Introducing chromadb for the Mixed Store

## Where we left off

`naive_rag` Lesson 20 replaced its hand-rolled list with `chromadb`
once linear scan stopped scaling. This course's mixed store has the
exact same shape (a list of `{text, embedding, source, modality, ...}`
records), so it graduates the same way, for the same reason: a real
`where`-filterable, real vector index instead of a Python list scanned
top to bottom on every query.

## The code, piece by piece

```python
collection.add(
    ids=[r["source"] for r in store],
    documents=[r["text"] for r in store],
    embeddings=[r["embedding"] for r in store],
    metadatas=[{"modality": r["modality"], "source": r["source"]} for r in store],
)
```

`naive_rag` Lesson 20's exact `.add()` call, with one new metadata key:
`"modality"`, alongside `"source"`, both plain strings, chromadb has no
special notion of "this metadata field matters", it stores whatever
dict of scalars it's given. This is what makes Lesson 21's `where`
filter possible next lesson, `modality` needs to exist as metadata
before it can be filtered on.

```python
results = collection.query(query_embeddings=[query_vector], n_results=3)
```

Unchanged from `naive_rag`. A caption's embedding and a text chunk's
embedding are the same shape (Lesson 5), so chromadb's index doesn't
need to know or care which is which to rank them together, the exact
same claim Lesson 7 already proved with a Python list, now true of a
real vector database too.

## Running it

```bash
uv run python lessons/multimodal_rag/03_advanced/20_introducing_chromadb_for_the_mixed_store/lesson.py
```

## Expected output

```
Collection has 9 documents

Query: "What's the torque spec for the derailleur hanger bolt?"
Top match: derailleur-hanger-diagram.png (modality=image, distance=0.XXXX)
```

## Checkpoint

- The mixed store's record shape maps onto chromadb exactly the way
  `naive_rag`'s text-only store did, `modality` is just one more
  metadata field alongside `source`.
- Nothing about ranking changes moving from a Python list to chromadb;
  what changes is what becomes possible next: real metadata filtering
  (Lesson 21) instead of a Python-level list comprehension.

If anything here still feels unclear, ask before moving to Lesson 21.
