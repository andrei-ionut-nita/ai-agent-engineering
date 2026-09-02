# Lesson 19: Where Per-Chunk Grading Gets Expensive

## Where we left off

Every lesson so far graded a handful of chunks, on a five-document
corpus, and it felt free. It isn't. Grading is an extra API call per
chunk (or per strip, since Lesson 10) on top of embedding and
generation, and this lesson measures what that actually costs, in real
seconds, then projects it to a corpus size this course's fixtures were
never meant to represent.

## The code, piece by piece

```python
n_samples = 3
start = time.perf_counter()
for _ in range(n_samples):
    grade_chunk(question, chunk_text)
elapsed = time.perf_counter() - start
per_call = elapsed / n_samples
```

A real, measured per-call latency, not a guessed number, the same
"measure it, don't assume it" instinct `naive_rag` Lesson 19 used for
timing linear scan.

```python
strips_per_chunk = 8
calls = k * strips_per_chunk
```

Strip-level grading (Lesson 10) multiplies the call count by roughly
however many strips a chunk splits into, here, 8, matching
`weather-station.md`'s own strip count from Lesson 10. That multiplier
is the real cost of the extra precision strip-level grading buys.

## Running it

```bash
uv run python lessons/corrective_rag/03_advanced/19_where_per_chunk_grading_gets_expensive/lesson.py
```

## Expected output

```
Measured 3 real grading calls in ~1.5s (~0.5s/call average)

Grading calls per question, whole-chunk grading (Lesson 3-9), over-fetched k, sequential:
  corpus=     5, k= 3:   3 grading call(s), ~1.5s if run one at a time
  corpus=   100, k=10:  10 grading call(s), ~5.1s if run one at a time
  corpus= 10000, k=20:  20 grading call(s), ~10.2s if run one at a time

Grading calls per question, STRIP-LEVEL grading (Lesson 10+), ~8 strips/chunk average:
  corpus=     5, k= 3:   24 grading call(s), ~12.3s if run one at a time
  corpus=   100, k=10:   80 grading call(s), ~40.9s if run one at a time
  corpus= 10000, k=20:  160 grading call(s), ~81.9s if run one at a time
```

The exact per-call latency varies by run and by network conditions, the
pattern that matters is the multiplier: strip-level grading costs
roughly 8x whole-chunk grading for the same `k`, and both scale with
`k`, not with corpus size directly, corpus size only matters insofar as
a bigger corpus tends to want a bigger `k` to stay confident it found
everything relevant.

If you've been running lessons back-to-back, you may see a much larger
per-call number here (several seconds instead of well under one), that's
this lesson's own `call_model()` backoff-and-retry kicking in after
hitting the free tier's requests-per-minute limit, not a bug, it's a
live demonstration of exactly the cost problem this lesson is about, and
the projections below scale from whatever real number you measured.

## Checkpoint

- Grading is not free, it's an extra model call per chunk (whole-chunk
  grading) or per strip (strip-level grading), on top of every embedding
  and generation call this pipeline already makes.
- The cost scales with `k` and, for strip-level grading, with how many
  strips a chunk splits into, not directly with corpus size.
- Two responses to this number, already partly built: Lesson 13's
  caching (skip re-grading identical question/chunk pairs) and Lesson
  20's cheap pre-filter (skip grading altogether for chunks a similarity
  threshold already rules out).

If anything here still feels unclear, ask before moving to Lesson 20.
