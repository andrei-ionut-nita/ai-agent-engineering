# Lesson 25: Advanced Capstone - A Complete Hybrid RAG Service

## What this is

No new concepts in this lesson. This is the course's capstone: a small,
real FastAPI service built entirely out of ideas from Lessons 1 through
24, combined into one thing. If you can read `lesson.py` and understand
why every piece is there, you've mastered this course.

## What it does

Ingests every fixture note into both a `chromadb` collection and a
`rank_bm25` index at startup, tagged with the category metadata from
Lesson 12. Serves `GET /ask`, which fuses dense and sparse rankings with
RRF, optionally scoped to a `category`, cites every source, and admits
when it doesn't know something.

## Where each piece came from

```python
dense_results = state.collection.query(
    query_embeddings=[query_vector], n_results=len(state.names), where=where,
)
```
Lesson 21 (`chromadb`-backed dense retrieval), plus Lesson 12's metadata
filter, passed straight through as chromadb's own `where` clause instead
of a manual Python filter, chromadb does the scoping natively.

```python
candidate_names = dense_ranking if category else state.names
sparse_ranking = sorted(candidate_names, key=lambda n: sparse_by_name[n], reverse=True)
```
`rank_bm25` has no built-in metadata filter, so the sparse side is
scoped by restricting which names it ranks to the same candidate set
dense already filtered to, keeping Lesson 12's rule (both retrievers see
an identical candidate pool) intact even though the two libraries handle
filtering differently.

```python
top_names = reciprocal_rank_fusion([dense_ranking, sparse_ranking])[:k]
```
Lesson 8's fusion, unchanged, now running on two real-library rankings
instead of hand-rolled ones.

## Running it

```bash
uv run python lessons/hybrid_rag/03_advanced/25_advanced_capstone_project/lesson.py
```

To run it as a real, live server: `uvicorn lesson:app --reload` from
this folder, then `curl "http://127.0.0.1:8000/ask?q=20240115"`.

## Expected output

```
GET /ask?{'q': '20240115'}
  {'answer': 'The firmware build 20240115 fixed an issue... (according to home_network.md).'}

GET /ask?{'q': "Why do vertical walls have ridges even though I didn't change any settings?"}
  {'answer': 'Vertical walls have ridges because of a worn brass nozzle... (according to 3d_printer.md).'}

GET /ask?{'q': 'Which build is the stable one?', 'category': 'network'}
  {'answer': 'Based on the provided context, the stable firmware build for the travel router is build 20210830 (according to old_travel_router.md).'}

GET /ask?{'q': 'What is the capital of France?'}
  {'answer': "I don't have information about that."}
```

## Known limitations (documented, not fixed here)

- **No relevance threshold.** Unlike `naive_rag`'s capstone, this service
  never checks whether the fused top-`k` results are actually good
  enough to answer from, it always answers with whatever it retrieves.
  Lesson 16's failure case (`"What change finally made things work
  reliably again?"`) will still confidently answer from the wrong
  document rather than admitting it doesn't know, retrieval ranked the
  wrong chunk highly, and nothing downstream catches that.
- **RRF's `k` is fixed at 60**, never tuned per query, per Lesson 11's
  finding that this course's own labeled set is too small to safely tune
  it at all.
- **The sparse index rebuilds from scratch on every server start**, no
  persistence (Lesson 13's pattern isn't wired into this service, it
  would need to run at import time rather than inside `ingest()`).

## Try this yourself

Without looking anything up:

- Rerun Lesson 16's exact question through this service's `/ask`
  endpoint. Does the answer confidently cite the wrong source, or hedge?
- Add a new fixture `.md` file with its own category, confirm it's
  retrievable both unscoped and scoped to its new category.
- Run `uvicorn lesson:app --reload` and hit `/ask` from a browser or
  `curl`, confirm it behaves identically to the `TestClient` calls above.

This is where Hybrid RAG, dense and sparse fused by hand and then by
real libraries, ends up: a small, real, citation-aware, filterable
service, with its failure modes written down rather than hidden. Lesson
26 is a short, code-free look at where this specific architecture still
falls short, and which course in this series picks up each thread.
