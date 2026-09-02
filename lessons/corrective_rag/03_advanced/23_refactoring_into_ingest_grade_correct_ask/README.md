# Lesson 23: Refactoring into ingest(), grade(), correct(), ask()

## Where we left off

Every lesson script so far has been one flat `main()`. This lesson draws
the same boundary `naive_rag` Lesson 23 and `hybrid_rag` Lesson 23 drew:
a clean separation between expensive one-time setup and cheap per-question
work, expressed as this series' shared **Strategy protocol**
(`docs/RAG-SERIES-PLAN/README.md`). This course also names its two
internal per-question steps, `grade()` and `correct()`, since they're
substantial enough on their own to deserve names, even though only
`ingest()` and `ask()` are the two functions the Strategy protocol
itself requires.

## The Strategy protocol, and what lives in this course's State

```python
class Strategy(Protocol):
    def ingest(self, docs: list[Path]) -> object: ...   # returns opaque State
    def ask(self, query: str, state: object, k: int = 2) -> str: ...
```

This course's implementation:

```python
def ingest(notes_dir: Path) -> CorrectiveState: ...
def ask(query: str, state: CorrectiveState, k: int = 2) -> str: ...
```

**What's inside `CorrectiveState`, explicitly, so a future course (like
`adaptive_rag` Lesson 21) can wire this in without reading the rest of
this file:**

```python
@dataclass
class CorrectiveState:
    collection: chromadb.Collection  # the retrieval index (Lessons 2-9's vector store, graduated to chromadb)
    grader: Grader                   # the retrieval evaluator (Lessons 3, 12), packaged as a small object
```

Two fields, both required: `collection` is what `_retrieve()` queries,
`grader` is what `grade()` calls to score each retrieved chunk. Nothing
else, `ask()`'s rewrite step calls the module-level Gemini client
directly (the same `call_model()` helper every lesson has used), it
doesn't need its own slot in `State`.

## The code, piece by piece

```python
def grade(query: str, chunks: list[dict], grader: Grader) -> list[dict]:
    return [{**c, "grade": grader.grade(query, c["text"])} for c in chunks]
```

Lesson 4's grade-every-chunk logic, now a named function taking a
`Grader` instance instead of calling a bare module function.

```python
def correct(query: str, graded_chunks: list[dict], state: CorrectiveState, k: int) -> tuple[str, list[dict]]:
    relevant = [c for c in graded_chunks if c["grade"] == "relevant"]
    if relevant:
        return query, relevant
    rewritten = call_model(REWRITE_PROMPT.format(question=query)).strip()
    ...
```

Lessons 5-7's filter-or-rewrite logic, combined into one function:
filter first, and only fall through to a rewrite-and-re-retrieve if
nothing survived filtering. Returns both the *effective* query (possibly
rewritten) and the chunks generation should actually use, mirroring
Lesson 8's `effective_query` tracking.

```python
def ask(query: str, state: CorrectiveState, k: int = 2) -> str:
    retrieved = _retrieve(query, state.collection, k)
    graded = grade(query, retrieved, state.grader)
    effective_query, relevant = correct(query, graded, state, k)
    ...
```

The Strategy protocol's `ask()`: retrieve, grade, correct, generate,
four calls, each one a named step from a lesson you've already done.

## Running it

```bash
uv run python lessons/corrective_rag/03_advanced/23_refactoring_into_ingest_grade_correct_ask/lesson.py
```

## Expected output

```
Ingested 5 documents into chromadb

Q: Project Aurora's Raspberry Pi writes sensor readings to a SQLite file on its SD card. Where does that Raspberry Pi physically live in the house?
A: Based on the provided context, Project Aurora's Raspberry Pi physically lives on a small shelf next to the bookshelf in the study.

Q: What is the capital of France?
A: I don't have any information relevant to that question.
```

## Checkpoint

- **`ingest(notes_dir) -> CorrectiveState`**: build-the-index, run once.
  **`ask(query, state, k=2) -> str`**: answer-a-question, run per
  question. This is the series' shared Strategy shape, matching
  `naive_rag` and `hybrid_rag` Lesson 23's exact two-function boundary.
- **`State = (collection, grader)`**, explicitly: a chromadb collection
  for retrieval, a `Grader` object for correction. That's the whole
  contract a future course needs to know to wire this course's retriever
  in without reading `grade()` or `correct()`'s internals.
- `grade()` and `correct()` are this course's own named internal steps,
  not part of the cross-course Strategy protocol itself, they exist
  because this course's per-question work is substantial enough to
  deserve names, the same way `hybrid_rag`'s RRF fusion logic lives
  inside its own `ask()` without becoming a third protocol function.

If anything here still feels unclear, ask before moving to Lesson 24.
