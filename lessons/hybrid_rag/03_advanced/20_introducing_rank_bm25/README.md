# Lesson 20: Introducing `rank_bm25`

## Where we left off

Lesson 19 showed exactly why this course's hand-rolled sparse scorer
degrades at scale: `idf()` rescans the whole corpus on every call, with
nothing cached. `rank_bm25` is a small, real BM25 implementation that
fixes precisely that, same algorithm from Lesson 5, precomputed
statistics instead of live rescans.

## The code, piece by piece

```python
from rank_bm25 import BM25Okapi

bm25 = BM25Okapi(tokenized_corpus)
```

Construction does the expensive part once: every document's length, the
corpus average length, and every term's document frequency, computed and
cached immediately. This is the missing piece from Lesson 19's hand-rolled
version, none of that was ever cached, it was recomputed inside the
scoring loop itself.

```python
scores = bm25.get_scores(query_tokens)
```

Every query after construction reuses that cached work. This is the
whole reason `rank_bm25` doesn't show the same runaway growth Lesson 19
measured, the expensive part already happened, once, up front.

## Running it

```bash
uv run python lessons/hybrid_rag/03_advanced/20_introducing_rank_bm25/lesson.py
```

## Expected output

```
Query: '20240115'
   1.296  home_network.md
   0.000  3d_printer.md
   ...

Query: 'Why is my espresso tasting sour and weak lately?'
   3.397  espresso_machine.md
   2.004  home_network.md
   ...
```

The exact scores differ from Lesson 5's hand-rolled version (`rank_bm25`
uses slightly different smoothing constants internally), but the
*ranking* matches: the right document wins both queries, same as every
earlier lesson found by hand. That's the point of graduating to a real
library here, not new behavior, the same behavior, without this course's
own implementation's scaling problem.

## Checkpoint

- **`rank_bm25`**: a real, small BM25 implementation, same algorithm as
  Lesson 5, with document statistics precomputed once at construction
  instead of rescanned on every call.
- **`BM25Okapi(tokenized_corpus)`**: the expensive setup step, done once.
- **`bm25.get_scores(query_tokens)`**: the cheap, repeatable query step,
  this is what actually runs per question in a real system.

If anything here still feels unclear, ask before moving to Lesson 21.
