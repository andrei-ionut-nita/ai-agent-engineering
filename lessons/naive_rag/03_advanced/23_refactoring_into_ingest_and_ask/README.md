# Lesson 23: Refactoring into ingest() and ask()

## Where we left off

Every lesson script so far has been one flat `main()`: build a store,
then run a query or two, top to bottom. That's fine for a lesson meant
to be read once, but not for a reusable piece of software, where
"building the index" and "answering a question" need to happen at
different times, possibly in different parts of a program entirely
(one at startup, the other on every incoming request). This lesson
draws that boundary explicitly, as two functions.

## Two functions, two responsibilities

```python
def ingest(notes_dir: Path, chroma_client) -> chromadb.Collection: ...
def ask(query: str, collection: chromadb.Collection, k: int = 2) -> str: ...
```

`ingest()` is everything this course has called "build the vector
store," start to finish: read documents, embed them, load them into a
collection. `ask()` is everything this course has called "answer a
question": embed the query, retrieve, generate. Nothing new is inside
either function, every line already existed somewhere in Lessons 6-21;
this lesson's only change is drawing a clean boundary between "setup"
and "per-question work," and naming each side.

## Why this boundary matters

`ingest()` is expensive (it makes an embedding API call for every
document) and only needs to run once. `ask()` is what runs, potentially,
thousands of times, once per question a user asks. Collapsing both into
one `main()`, as every earlier lesson did, hides that difference. Once
they're separate functions, it becomes obvious that `ingest()` belongs
at startup and `ask()` belongs wherever a question comes in, which is
exactly the shape Lesson 24's web service needs next.

## Running it

```bash
uv run python lessons/naive_rag/03_advanced/23_refactoring_into_ingest_and_ask/lesson.py
```

## Expected output

```
Ingested 5 documents

Q: What's the best way to get a crispy pizza crust?
A: <a grounded answer about 00 flour, cold ferment, preheated steel>

Q: What is the capital of France?
A: I don't have any information relevant to that question.
```

## Checkpoint

- **`ingest()`**: build-the-index, run once, expensive (real API calls).
- **`ask()`**: answer-a-question, run per question, meant to be called
  many times against the same already-built index.
- This `ingest(docs) -> State` / `ask(query, state, k) -> str` shape is
  the series' shared `Strategy` protocol (see
  `docs/RAG-SERIES-PLAN/README.md`), the convention courses 2-7 build
  their own retrievers against so a later course can wire several
  strategies in behind one router without reconciling five different
  signatures.
- Separating "setup" from "per-request work" into named functions is
  what makes the next lesson's web service possible without restructuring
  anything, `ingest()` runs at startup, `ask()` runs per request, exactly
  matching the shape they already have here.

If anything here still feels unclear, ask before moving to Lesson 24.
