# Lesson 13: Persisting Both Indexes

## Where we left off

Every lesson so far rebuilt both indexes, dense and sparse, from scratch
on every run, embedding every document over again even though nothing
changed. `naive_rag` Lesson 13 fixed this for a single vector store;
this lesson does the same thing for both halves of a hybrid index at
once.

## The code, piece by piece

```python
def build_store() -> dict:
    return {
        "names": names,
        "token_lists": [tokenize(text) for text in texts],
        "doc_vectors": embed_texts(texts),
    }
```

One dict, both indexes. `token_lists` costs nothing to rebuild, it's
just tokenizing text, no API call involved. `doc_vectors` is the
expensive part, one embedding call per document, and the only reason
this lesson exists: there's no benefit to persisting the sparse half on
its own, but persisting *both* together means one save/load pair covers
the whole hybrid index instead of two separate mechanisms.

```python
def save_store(store: dict, path: Path) -> None:
    path.write_text(json.dumps(store))
```

Same trick as `naive_rag` Lesson 13: a dict of lists of floats and
strings is exactly what JSON already represents, no custom
serialization needed for either index.

## Running it

```bash
uv run python lessons/hybrid_rag/02_intermediate/13_persisting_both_indexes/lesson.py
```

Run it twice. The first run has no `store.json` yet, so it embeds every
document and saves the result. The second run loads that same file
instead.

## Expected output

First run:
```
Built dense + sparse indexes for 6 documents and saved to store.json in 0.8812s
```

Second run:
```
Loaded 6 documents (dense + sparse) from store.json in 0.0005s
(zero embedding calls made, delete store.json to force a rebuild)
```

Roughly a thousand-fold difference, and the second run makes zero calls
to Gemini's embedding endpoint at all, the sparse index was already free
to rebuild, so all of that savings comes from skipping the dense half's
API calls specifically.

## Checkpoint

- Persisting a hybrid index means persisting *both* halves together,
  the sparse index is cheap to rebuild on its own, but bundling it with
  the dense index means one file, one load, one hybrid-ready store.
- The dense half is where persistence actually pays off, embedding API
  calls are the expensive, worth-skipping part.
- Delete `store.json` to force a full rebuild, the same escape hatch
  `naive_rag` Lesson 13 used.

If anything here still feels unclear, ask before moving to Lesson 14.
