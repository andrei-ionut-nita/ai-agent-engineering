# Lesson 21: Persisting and Loading Indexes

## The cost Lesson 4 flagged, paid off

Lesson 4 pointed out that `VectorStoreIndex.from_documents()` makes one
embedding API call per Node, and that indexing cost scales with node
count, not document count. Every lesson in this course since then has
paid that cost fresh on every single run, rebuilding the same three-file
Nimbus index from scratch each time. That's fine at fixture-data scale,
but it doesn't survive contact with a real corpus or a real
application, you don't want to re-embed thousands of Nodes every time a
script restarts.

`StorageContext.persist()` and `load_index_from_storage()` are the fix:
write an index's Nodes, vectors, and internal structure to plain JSON
files on disk once, then reload from those files as many times as you
want, with zero new embedding calls for anything already stored.

## What actually gets written

`index.storage_context.persist(persist_dir=...)` writes three JSON
files into the target folder:

- `docstore.json`: every Node's text and metadata.
- `index_store.json`: the index's internal structure (which Nodes it
  has, how they're organized).
- `default__vector_store.json`: every Node's embedding vector.

Reloading with `load_index_from_storage()` reads all three back and
reconstructs the exact same `VectorStoreIndex` object you had before
persisting, Nodes, vectors, and all.

## This lesson's script simulates two processes in one file

`build_and_persist()` plays the role of a first process: load the
Nimbus policy documents, build a fresh index (paying the embedding
cost), and persist it. `load_and_query()` plays the role of a second,
later process: it never touches `SimpleDirectoryReader` or
`from_documents()`, it only reads `./storage/` back with
`StorageContext.from_defaults(persist_dir=...)` and
`load_index_from_storage()`, then queries the reloaded index directly.
Both functions run in the same `main()` here for a single runnable demo,
but nothing about `load_and_query()` depends on `build_and_persist()`
having run in the same process, that's the whole point.

## Build artifact, not course content

This lesson writes a `./storage/` subfolder next to `lesson.py`, in the
lesson's own directory. It's a build artifact produced by running the
script, not hand-authored course content. **Re-running this script is
idempotent**: it always rebuilds the index from the same three source
`.txt` files and overwrites `./storage/` with equivalent content each
time. The one thing that differs between runs is each Node's `node_id`
(a random UUID assigned at split time), so the JSON files' exact bytes
change run to run, but the text, structure, and query behavior reloaded
from them are identical.

## The code, piece by piece

```python
index.storage_context.persist(persist_dir=str(STORAGE_DIR))
```

Every `VectorStoreIndex` already carries a `storage_context` (created
automatically inside `from_documents()`), `persist()` is a method on
that, not a separate top-level call.

```python
storage_context = StorageContext.from_defaults(persist_dir=str(STORAGE_DIR))
reloaded_index = load_index_from_storage(storage_context)
```

The reload path: construct a fresh `StorageContext` pointed at the
persisted folder, then hand it to `load_index_from_storage()`, which
reads the JSON files and reconstructs the index object. Note this
reads `Settings.embed_model`'s configuration implicitly (Lesson 3's
global pattern) but doesn't call it for anything already stored.

```python
response = query_engine.query(question)
```

Querying a reloaded index still costs exactly one embedding call, to
embed the incoming question so it can be compared against the
already-stored Node vectors. What's avoided is re-embedding the stored
Nodes themselves, the cost that scales with corpus size.

## Running it

```bash
uv run python lessons/llamaindex/03_advanced/21_persisting_and_loading_indexes/lesson.py
```

## Expected output

No LLM wording variance to speak of here (the answer is a single
factual lookup), captured from a real run, exact:

```
Built index: 3 nodes (this cost embedding API calls)
Persisted to lessons/llamaindex/03_advanced/21_persisting_and_loading_indexes/storage

Reloaded index: 3 nodes (zero embedding calls for these)

Q: How many paid public holidays does Nimbus Robotics observe?
A: Nimbus Robotics observes 10 paid public holidays per year.
```

## Checkpoint

- **`index.storage_context.persist(persist_dir=...)`**: writes an
  index's Nodes, structure, and vectors to JSON files on disk.
- **`StorageContext.from_defaults(persist_dir=...)` +
  `load_index_from_storage()`**: reconstructs the same index from those
  files, zero new embedding calls for already-stored Nodes.
- Querying a reloaded index still costs one embedding call, for the
  incoming question itself, that part is unavoidable.
- This lesson's `./storage/` folder is a regenerable build artifact;
  re-running the script is idempotent (same source data in, equivalent
  index out, only random Node IDs differ between runs).

If anything here still feels unclear, ask before moving to Lesson 22.
