# Lesson 8: End-to-End Corrective Q&A

## What we're building

No new concepts. This lesson assembles Lessons 2-7 into one function,
`corrective_ask()`, retrieve, grade, filter, rewrite-and-re-retrieve if
needed, generate. Every line already existed in an earlier lesson; this
lesson's only job is wiring them together into one pipeline a single
question can flow through end to end.

## The pipeline, piece by piece

```python
def corrective_ask(query: str, store: list[dict], k: int = 3) -> str:
    retrieved = retrieve(query, store, k)
    graded = grade_all(query, retrieved)
    relevant = [chunk for chunk in graded if chunk["grade"] == "relevant"]
```

Steps 1-3: over-fetch (Lesson 4), grade everything retrieved (Lesson 4),
filter to what's relevant (Lesson 5). This alone already fixes this
course's running example, the correct chunk was retrieved, just
outranked.

```python
    effective_query = query
    if not relevant:
        effective_query = rewrite_query(query)
        retrieved = retrieve(effective_query, store, k)
        graded = grade_all(effective_query, retrieved)
        relevant = [chunk for chunk in graded if chunk["grade"] == "relevant"]
```

Step 4, only reached if filtering left nothing: rewrite the query
(Lesson 6), then repeat retrieval and grading against the rewritten
version (Lesson 7). This branch is what fires for a genuinely
all-not-relevant top-k, whether or not the rewrite manages to fix it.

```python
    return generate_answer(effective_query, relevant)
```

Step 5: generate from whatever survived. `effective_query` is the
rewritten wording if a rewrite happened, generation should use the
clearer version of the question too, not just retrieval. If nothing
ever became relevant (the France case), `relevant` is an empty list,
and `generate_answer` returns the honest "I don't have any information"
fallback without spending a generation call on an empty context.

## Running it

```bash
uv run python lessons/corrective_rag/01_beginner/08_end_to_end_corrective_qa/lesson.py
```

## Expected output

```
Q: Project Aurora's Raspberry Pi writes sensor readings to a SQLite file on its SD card. Where does that Raspberry Pi physically live in the house?
A: Based on the context provided, Project Aurora's Raspberry Pi lives on a small shelf next to the bookshelf in the study...

Q: What is the capital of France?
    (no relevant chunks, rewrote query to: 'What is the capital of France?')
A: I don't have any information relevant to that question.
```

The first answer is the corrected, grounded answer bookshelf.md
actually supports, fixed by filtering alone, no rewrite fired. The
second question triggers the rewrite branch (every top-3 chunk graded
not-relevant), and honestly reports that no correction, wording-level or
otherwise, can produce an answer this corpus was never going to contain.

## Checkpoint

- `corrective_ask()` is Lessons 2-7, wired together: nothing new, one
  clear boundary between "setup" (the vector store) and "per-question
  work" (everything else), the same shape `naive_rag`'s Lesson 8 used.
- Two distinct outcomes for the same pipeline: correction that succeeds
  (filtering finds a better-graded chunk) and correction that honestly
  fails (rewriting can't invent missing knowledge). Both are correct
  behavior, not bugs.
- Lesson 9 wraps this exact function in a small CLI, so you can ask it
  your own questions instead of the three built into this script.

If anything here still feels unclear, ask before moving to Lesson 9.
