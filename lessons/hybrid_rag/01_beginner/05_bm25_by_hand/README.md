# Lesson 5: BM25 by Hand

## Where we left off

TF-IDF (Lesson 4) has a quiet flaw: a term's contribution to the score
grows *linearly* with how many times it appears. A document that
mentions a word twice scores exactly twice as high on that term as one
that mentions it once, four times scores four times as high, and so on,
forever. In practice, that's wrong: a document mentioning "firmware"
five times isn't five times more about firmware than one mentioning it
once, at some point it's just a longer, more repetitive document.

**BM25** (Best Match 25) fixes this with two changes: term-frequency
**saturation** (each additional occurrence of a term matters less than
the last) and **length normalization** (a longer document doesn't win
just by containing more words overall). It's the sparse-retrieval
algorithm actually used in production search engines, and the direct
ancestor of `rank_bm25`, the library this course graduates to in the
Advanced tier.

## The code, piece by piece

```python
numerator = tf * (K1 + 1)
denominator = tf + K1 * (1 - B + B * doc_len / avg_doc_len)
score += term_idf * (numerator / denominator)
```

`K1` (1.5 here, the standard default) controls how fast saturation
kicks in. `B` (0.75) controls how much document length matters, `B=0`
would turn length normalization off entirely, `B=1` would make it fully
proportional to length. `doc_len / avg_doc_len` is where a document
longer than average gets its score pulled down slightly, one shorter
than average gets a small boost, correcting for length instead of
rewarding it.

## Running it

```bash
uv run python lessons/hybrid_rag/01_beginner/05_bm25_by_hand/lesson.py
```

## Expected output

```
Query: 'Why does it happen and what should I do about it?'
   3.286  home_network.md
   2.674  3d_printer.md
   1.425  bike_maintenance.md
   0.792  old_travel_router.md
   0.788  houseplants.md
   0.331  espresso_machine.md

Query: 'What is firmware build 20240115 for?'
   6.432  home_network.md
   4.158  old_travel_router.md
   1.288  espresso_machine.md
   1.233  3d_printer.md
   0.245  houseplants.md
   0.000  bike_maintenance.md

term frequency -> TF-IDF contribution vs. BM25 contribution (same idf, avg-length doc):
  tf= 1   TF-IDF=  2.00   BM25= 2.00
  tf= 2   TF-IDF=  4.00   BM25= 2.86
  tf= 4   TF-IDF=  8.00   BM25= 3.64
  tf= 8   TF-IDF= 16.00   BM25= 4.21
  tf=16   TF-IDF= 32.00   BM25= 4.57
  tf=32   TF-IDF= 64.00   BM25= 4.78
```

The rankings on this course's six short, similar-length documents look
close to Lesson 4's TF-IDF rankings, this corpus doesn't have enough
length variance to show off length normalization clearly (the firmware
question's ranking still isn't a clean tie the way Lesson 3's raw count
was, IDF alone already fixed that in Lesson 4). The saturation curve at
the bottom is the real point, and it's stark: at
`tf=1`, TF-IDF and BM25 agree exactly. By `tf=32`, TF-IDF has grown to
64 (still perfectly linear, 32x the `tf=1` value), while BM25 has
leveled off just under 5, because after a handful of repetitions,
another occurrence of the same word tells you almost nothing new about
what the document is about.

## Checkpoint

- **BM25**: TF-IDF plus term-frequency saturation and document-length
  normalization, the sparse-retrieval algorithm production search
  engines actually use.
- **`k1`**: controls how fast repeated terms stop adding much to the
  score.
- **`b`**: controls how strongly document length is corrected for, `0`
  disables it, `1` makes it fully proportional.
- Lesson 20 replaces this hand-rolled version with `rank_bm25`, same
  algorithm, a real library.

If anything here still feels unclear, ask before moving to Lesson 6.
