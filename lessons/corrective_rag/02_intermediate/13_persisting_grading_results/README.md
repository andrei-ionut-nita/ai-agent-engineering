# Lesson 13: Persisting Grading Results

## Where we left off

Every lesson so far re-graded the same chunks from scratch on every run.
That's fine for a lesson meant to be read once, but a real system asking
the same or similar questions repeatedly would waste an API call
re-grading a (question, chunk) pair it already graded identically
before. `naive_rag` Lesson 13 persisted embeddings the same way, for
the same reason, grading results deserve the same treatment.

## The code, piece by piece

```python
def cache_key(question: str, chunk_text: str) -> str:
    digest = hashlib.sha256(f"{question}\n---\n{chunk_text}".encode()).hexdigest()
    return digest
```

A grade is a function of *both* the question and the exact chunk text,
change either one and it's a genuinely different grading decision, not
a cache hit. Hashing both together into one key means the cache stays
correct even if the same question is asked against different chunks, or
the same chunk is graded against different questions.

```python
def grade_chunk_cached(question: str, chunk_text: str, cache: dict[str, str]) -> tuple[str, bool]:
    key = cache_key(question, chunk_text)
    if key in cache:
        return cache[key], True
    ...
```

Check the cache first, only call the model on a miss. The `bool` in the
return value exists purely so this lesson can show you which happened,
a real system wouldn't need it.

## Running it

```bash
uv run python lessons/corrective_rag/02_intermediate/13_persisting_grading_results/lesson.py
```

## Expected output

First run (no `grade_cache.json` yet):

```
Cache loaded from grade_cache.json: 0 entries

Run 1: grade='relevant', source=Gemini API call
Run 2: grade='relevant', source=cache

Saved 1 grading result(s) to grade_cache.json. ...
```

Second run (`grade_cache.json` now exists):

```
Cache loaded from grade_cache.json: 1 entry

Run 1: grade='relevant', source=cache
Run 2: grade='relevant', source=cache
...
```

Delete `grade_cache.json` to force re-grading from scratch.

## Checkpoint

- Grading results are cheap to persist and expensive to recompute
  needlessly, the same "don't redo real API work every run" idea as
  `naive_rag` Lesson 13's embedding cache.
- A cache key needs to capture everything a grade actually depends on
  (here, question *and* chunk text), a key missing either piece would
  return a stale grade for a genuinely different question or chunk.
- This is a small-scale preview of Lesson 19's real subject, at real
  scale, grading every chunk on every query gets expensive fast, and
  caching is one of several mitigations that lesson puts a number on.

If anything here still feels unclear, ask before moving to Lesson 14.
