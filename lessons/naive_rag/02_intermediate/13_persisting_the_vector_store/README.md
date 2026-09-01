# Lesson 13: Persisting the Vector Store

## Where we left off

Every lesson so far rebuilds the vector store from scratch, embedding
every chunk again, every single time the script runs. That's wasteful
(each run burns embedding calls against a rate-limited free tier for
work that produced the exact same result last time) and it means an
in-memory Python list, true to its name, vanishes the moment the
program exits. This lesson fixes both with the simplest possible
persistence: a JSON file.

## Why JSON is enough here

A vector, underneath the abstraction, is just a list of floating-point
numbers. A vector store, in this course, is just a list of dicts. JSON
already knows how to represent exactly those two things, lists and
dicts of strings/numbers, with no translation step needed:

```python
path.write_text(json.dumps(store))
```

This won't scale to millions of records (loading the whole file back
into memory becomes slow and memory-hungry well before that point), but
for the handful of documents this course works with, it's a complete,
honest answer to "how do I not lose my embeddings when the program
exits."

## The code, piece by piece

```python
def save_store(store: list[dict], path: Path) -> None:
    path.write_text(json.dumps(store))

def load_store(path: Path) -> list[dict]:
    return json.loads(path.read_text())
```

Two small, symmetric functions. `save_store` turns the Python list into
a JSON string and writes it to disk; `load_store` reads that string back
and turns it back into the exact same Python list, floats and all.

```python
if STORE_PATH.exists():
    store = load_store(STORE_PATH)
    ...
else:
    store = build_vector_store()
    save_store(store, STORE_PATH)
```

The pattern every persistence layer follows in some form: check if saved
data exists first, load it if so; only do the expensive work (embedding,
here) if it doesn't.

## Running it

```bash
uv run python lessons/naive_rag/02_intermediate/13_persisting_the_vector_store/lesson.py
```

Run it twice, in order. The first time, no `store.json` exists yet, so
it embeds and saves. The second time, `store.json` already exists, so
it loads from disk instead, with no embedding calls and a load time
several orders of magnitude faster.

## Expected output

First run:
```
Embedded 5 records and saved to store.json in 0.9xxxs
```

Second run:
```
Loaded 5 records from store.json in 0.0xxxs
(no embedding calls made, delete store.json to force re-embedding)
```

Delete `store.json` (it's gitignored, safe to remove any time) to see
the first-run behavior again.

## Checkpoint

- **persistence**: saving the vector store to disk so it survives the
  program exiting, instead of rebuilding it from scratch every run.
- A vector store's contents (lists and dicts of numbers and strings) map
  directly onto JSON, no special serialization format needed at this
  scale.
- Check-then-build-or-load is the general shape of caching: do the
  expensive work once, reuse the result afterward until something
  invalidates it.

If anything here still feels unclear, ask before moving to Lesson 14.
