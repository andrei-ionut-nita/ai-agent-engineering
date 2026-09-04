# Lesson 22: Refactoring into ingest() and ask()

## Where we left off

`naive_rag` Lesson 23 collapsed its whole pipeline into two functions:
`ingest()` (run once, build the index) and `ask()` (run per question).
This lesson does the same collapse here, and the result is this
course's implementation of the RAG-architecture series' shared
`Strategy` protocol (`docs/RAG-SERIES-PLAN/README.md`): any course in
this series can be swapped in behind the same two-function shape, as
long as it provides `ingest(docs) -> State` and `ask(query, state, k)
-> str`. This lesson is what makes `multimodal_rag` compatible with
that shape.

## What `State` is, here

```python
def ingest(notes_dir: Path, images_dir: Path, chroma_client) -> chromadb.Collection:
    ...
```

`State` for this course is a single `chromadb.Collection`, exactly like
`naive_rag`'s, holding **both modalities together**: every record's
`documents` entry is a caption (for images) or a chunk (for text), and
every record's `metadatas` entry carries `modality` (`"text"` or
`"image"`), `source` (the original filename), and `image_path` (the
absolute path to the original file, an empty string for text records,
since chromadb metadata values must be scalars, `None` isn't
representable). Nothing in `State` distinguishes "this collection is
for multimodal_rag" from any other course's collection, structurally,
that's the whole point: a caller consuming `State` through `ask()`
alone doesn't need to know this course produced it, only that it's a
`chromadb.Collection` shaped the way this protocol expects. This is
exactly what `adaptive_rag` Lesson 21 (a later course in this series)
needs to wire this course in as one of several retrieval strategies it
routes between, without reading this course's full implementation, only
this README's description of `State`.

## The code, piece by piece

```python
def ask(query: str, collection: chromadb.Collection, k: int = 2) -> str:
    query_vector = embed_texts([query])[0]
    results = collection.query(
        query_embeddings=[query_vector], n_results=k, include=["documents", "metadatas"]
    )
    ...
    for document, metadata in zip(documents, metadatas):
        if metadata["image_path"]:
            image_bytes = Path(metadata["image_path"]).read_bytes()
            parts.append(types.Part.from_bytes(data=image_bytes, mime_type="image/png"))
        else:
            parts.append(document)
```

Everything this course built, Lesson 8's re-attach-the-original-image
idea, Lesson 14's modality-aware citation prompt, collapses into this
one function. `metadata["image_path"]` (truthy or empty string) plays
the exact role `record["image_path"] is not None` played back in Lesson
6, just expressed as chromadb-compatible metadata instead of a Python
`None`.

## Running it

```bash
uv run python lessons/multimodal_rag/03_advanced/22_refactoring_into_ingest_and_ask/lesson.py
```

## Expected output

```
Ingested 9 documents

Q: What's the torque spec for the derailleur hanger bolt?
A: <a grounded answer citing the image, mentioning 8 Nm>

Q: What is the capital of France?
A: <an honest admission the retrieved context doesn't answer this, not a guess>
```

## Checkpoint

- **`State`** for this course: a `chromadb.Collection` whose
  `metadatas` carry `modality`, `source`, and `image_path` (empty
  string for text) on every record, both modalities in one collection.
- `ingest(docs) -> State`, `ask(query, state, k) -> str`: this course's
  implementation of the series' shared `Strategy` protocol, callable by
  any later course without reading past this description of `State`.
- Everything from Lessons 1-21 is still present, just organized behind
  two functions instead of scattered across a script's `main()`.

If anything here still feels unclear, ask before moving to Lesson 23.
