# Lesson 23: Refactoring into ingest() and ask()

## Where we left off

Every lesson script so far has been one flat `main()`. This lesson draws
the same boundary `naive_rag` Lesson 23 drew: `ingest()` (expensive,
runs once) and `ask()` (cheap, runs per question), the shape this
course's Advanced tier has been building toward since Lesson 13's
persistence.

## Why this shape specifically

This course's `ingest()`/`ask()` isn't just a local convenience, it's
the series' shared `Strategy` protocol
(`docs/RAG-SERIES-PLAN/README.md`): `ingest(docs) -> State`,
`ask(query, state, k) -> str`. `naive_rag`'s own Lesson 23 already
implements this shape for dense-only retrieval; this course does the
same for hybrid. The point of standardizing this now is course 7,
Adaptive RAG, which wires in real Advanced-tier implementations from
every prior course behind one router, that only works cleanly if every
course's `ask()` already has the same shape.

## The code, piece by piece

```python
class HybridState:
    def __init__(self, collection, bm25, names, texts):
        self.collection = collection
        self.bm25 = bm25
        self.names = names
        self.texts = texts
```

This course's `State`: a chromadb collection for the dense half, a
`BM25Okapi` index plus the raw texts for the sparse half. Everything
`ask()` needs, built once by `ingest()`.

```python
def ingest(notes_dir: Path) -> HybridState: ...
def ask(query: str, state: HybridState, k: int = 2) -> str: ...
```

Lessons 21's dense+sparse setup collapses into `ingest()`. Lesson 21's
retrieve-fuse-generate collapses into `ask()`. Nothing new is inside
either function, every line already existed somewhere in Lessons 20-22.

## Running it

```bash
uv run python lessons/hybrid_rag/03_advanced/23_refactoring_into_ingest_and_ask/lesson.py
```

## Expected output

```
Ingested 6 documents (dense + sparse)

Q: 20240115
A: Based on the provided context, firmware build 20240115 is the TP-Link Archer AX55 v3 router firmware build that fixed the issue of the router silently dropping the 5GHz radio when more than eight devices were connected at once [home_network.md].

Q: What is the capital of France?
A: The context doesn't contain the answer, so I cannot guess.
```

## Checkpoint

- **`ingest(docs) -> State`**: build both indexes once, expensive, real
  API calls.
- **`ask(query, state, k) -> str`**: answer one question, cheap, meant to
  run many times against the same state.
- This exact shape is the series' shared `Strategy` protocol, the reason
  `adaptive_rag` (course 7) can compose this course's hybrid retrieval
  with every other course's strategy behind one router later.

If anything here still feels unclear, ask before moving to Lesson 24.
