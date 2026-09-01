# Lesson 9: Beginner Checkpoint - Hybrid Search CLI

## What this is

No new concepts in this lesson. This is a checkpoint: a small, real
script built entirely out of ideas from Lessons 1 through 8, combined
into one thing. If you can read `lesson.py` and understand why every
piece is there, you've mastered the Beginner tier. If any piece feels
unfamiliar, that's a sign to revisit the lesson it came from before
continuing to Intermediate.

## What it does

Builds two independent indexes over this course's six fixture notes,
one dense (embeddings, Lessons 1-2), one sparse (BM25, Lessons 3-5),
then answers four questions by fusing both rankings with RRF (Lesson 8)
before generating an answer. Two of the questions are the bare-ID kind
sparse is built for, two are the paraphrased kind dense is built for,
deliberately chosen so no single retriever alone could answer all four.

## Where each piece came from

```python
def build_store(notes_dir: Path) -> dict:
    return {"names": ..., "texts": ..., "token_lists": ..., "doc_vectors": ...}
```
One store, both indexes: tokenized text for BM25 (Lesson 3), embeddings
for cosine similarity (Lesson 2), built once, queried many times.

```python
def hybrid_retrieve(query: str, store: dict, k: int = 2) -> list[str]:
    dense = dense_ranking(query_vector, store)
    sparse = sparse_ranking(query, store)
    fused = reciprocal_rank_fusion([dense, sparse])
    return fused[:k]
```
Lesson 8's fusion, unchanged: rank both ways, fuse by rank alone, no
weight to tune, no scores to normalize.

```python
def ask(query: str, store: dict, k: int = 2) -> str:
    top_names = hybrid_retrieve(query, store, k)
    return generate(query, top_names, store)
```
The whole pipeline as one function call, same shape as `naive_rag`
Lesson 9's `ask()`, just with a hybrid retriever underneath instead of a
dense-only one.

## Running it

```bash
uv run python lessons/hybrid_rag/01_beginner/09_beginner_checkpoint_project/lesson.py
```

You should see all four questions answered correctly and cited: a
torque spec and a firmware build number (bare IDs, sparse's strength),
then an espresso and a 3D-printing question (pure paraphrase, dense's
strength), all through the exact same `ask()` call.

## Try this yourself

Without looking anything up:

- Ask `ask("20240115", store)` with `k=1` instead of `2`. Does it still
  get the right document, or does shrinking `k` to one slot make the
  fusion less forgiving?
- Add a fifth demo question, paraphrased, with the answer inside
  `old_travel_router.md` specifically (the confusable router note). Does
  hybrid retrieval get it right where Lesson 1's dense-only demo
  struggled?
- Temporarily change `hybrid_retrieve` to return only `dense[:k]` (skip
  the fusion entirely) and rerun. Which of the four questions breaks?

If you can make these changes confidently, you're ready for the
Intermediate tier, starting at Lesson 10.
