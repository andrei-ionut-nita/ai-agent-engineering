# Lesson 25: Advanced Capstone - A Complete Corrective RAG Service

## What this is

No new concepts in this lesson. This is the course's capstone: a small,
real FastAPI service built entirely out of ideas from Lessons 1 through
24, combined into one thing. If you can read `lesson.py` and understand
why every piece is there, you've mastered this course. If any piece
feels unfamiliar, that's a sign to revisit the lesson it came from.

## What it does

Ingests every fixture note into a chromadb collection at startup
(Lesson 23), then serves a `GET /ask` endpoint that: pre-filters
candidates by similarity score (Lesson 20), grades what survives
(Lessons 3, 12), bounded-rewrites and re-retrieves if nothing graded
relevant (Lessons 6-7, 21), falls back to external search if the bound
is hit (Lesson 22), and cites its source in every answer (Lesson 15).

## Where each piece came from

```python
candidates = [c for c in chunks if c["score"] >= PRE_FILTER_MIN_SCORE]
graded = [{**c, "grade": grader.grade(query, c["text"])} for c in candidates]
```
Lesson 20's pre-filter, run before Lesson 3/12's real LLM grading, to
cut grading calls on obviously-unrelated candidates.

```python
while not relevant and attempts < MAX_REWRITE_ATTEMPTS:
    effective_query = call_model(REWRITE_PROMPT.format(question=effective_query)).strip()
    ...
    attempts += 1
```
Lesson 21's bounded rewrite loop. `MAX_REWRITE_ATTEMPTS = 1` here
(smaller than Lesson 21's own `2`), kept low specifically so a live
service doesn't spend unbounded grading calls per incoming request,
this course's Lesson 19 cost lesson, applied.

```python
if relevant:
    ...
else:
    web_result = external_search(query)
```
Lesson 22's real "incorrect" branch: once the bound is hit, fall
through to external search (mocked here, pluggable in a real
deployment) instead of giving up or looping forever.

```python
context = "\n\n".join(f"[{c['source']}]\n{c['text']}" for c in relevant)
...
prompt = f"""...citing the source in brackets like [source.md] or [external web search]..."""
```
Lesson 15's citation format, extended to also credit
`[external web search]` when that branch fires, so a user can always
tell where an answer actually came from.

## Running it

```bash
uv run python lessons/corrective_rag/03_advanced/25_advanced_capstone_project/lesson.py
```

To run it as a real, live server: `uvicorn lesson:app --reload` from
this folder, then `curl "http://127.0.0.1:8000/ask?q=..."`.

## Expected output

```
GET /ask?q="Project Aurora's Raspberry Pi writes sensor readings to a SQLite file on its SD card. Where does that Raspberry Pi physically live in the house?"
  {'answer': "Based on the provided notes collection, Project Aurora's Raspberry Pi physically lives in the study, on a small shelf next to the bookshelf [bookshelf.md]."}

GET /ask?q='What is the capital of France?'
  {'answer': 'Based on the provided context, the capital city of France is Paris [external web search].'}
```

The first question resolves entirely internally, with correction fixing
naive retrieval's confident miss (this course's running example since
Lesson 2). The second resolves externally, this course's very first
unanswerable question (Lesson 1) finally gets a real, cited answer.

## Try this yourself

Without looking anything up:

- Set `MAX_REWRITE_ATTEMPTS = 0` and re-run. Does the France question
  now go straight to external search without ever attempting an
  internal rewrite? Does that change anything about the Aurora
  question's outcome?
- Swap `mock_web_search` for a function that always returns `None`.
  Confirm the France question now returns the honest "internally or
  externally" failure message from Lesson 21/22 instead of an answer.
- Run `uvicorn lesson:app --reload` from this folder and hit `GET
  /ask?q=...` from a browser or `curl`, confirm it behaves identically
  to the `TestClient` calls in the script.

This is where Corrective RAG, built entirely from scratch, ends up: a
small, real, citation-aware service that grades what it retrieves and
corrects it, internally or externally, before ever answering. Lesson 26
is a short, code-free look at where this specific architecture still
falls short, and which course in this series picks up each of those
threads.
