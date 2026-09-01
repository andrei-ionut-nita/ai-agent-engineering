# Lesson 8: Reciprocal Rank Fusion

## Where we left off

Lesson 7 fused dense and sparse *scores*, which meant normalizing two
incomparable scales and then tuning a weight against a labeled set, the
same fragile pattern flagged for any hyperparameter tuned against a
small eval set. **Reciprocal Rank Fusion (RRF)** sidesteps both
problems at once: it never looks at scores, only at *rank*, which
document came first, second, third in each retriever's own ranking.

## The code, piece by piece

```python
def reciprocal_rank_fusion(rankings: list[list[str]], k: int = 60) -> list[str]:
    rrf_scores = {}
    for ranking in rankings:
        for rank, name in enumerate(ranking, start=1):
            rrf_scores[name] = rrf_scores.get(name, 0.0) + 1 / (k + rank)
    return sorted(rrf_scores, key=lambda name: rrf_scores[name], reverse=True)
```

For every ranking (dense, sparse, or more if there were more), each
document gets `1 / (k + its rank in that ranking)`. Rank 1 contributes
the most, rank 6 the least, and a document that doesn't appear in a
ranking at all (dropped below the cutoff, in a fuller system) simply
contributes zero from that side. Sum a document's contributions across
every ranking, sort by the total, done. No score from dense is ever
compared to a score from sparse, because neither score is used at all,
only where each document landed.

`k` (the constant, unrelated to top-`k` retrieval's `k`) softens how
much rank 1 dominates over rank 2; a large `k` makes the difference
between ranks small, a small `k` makes it sharp. `60` is the standard
default from the original RRF paper, and this course leaves it there
until Lesson 11 examines it directly.

## Running it

```bash
uv run python lessons/hybrid_rag/01_beginner/08_reciprocal_rank_fusion/lesson.py
```

## Expected output

```
lexical   HIT    '20240115'   dense#1=old_travel_router.md  sparse#1=home_network.md  fused#1=home_network.md
...
semantic  HIT    "Why do vertical walls have ridges..."  dense#1=3d_printer.md  sparse#1=home_network.md  fused#1=3d_printer.md
...
RRF (no weight tuned, no scores normalized): 10/10  (lexical: 5/5, semantic: 5/5)
```

Look at that first row: dense alone picked the wrong document
(`old_travel_router.md`), the exact miss from Lesson 6. But sparse
ranked the right one (`home_network.md`) first, and RRF's fused ranking
follows sparse here, not because anyone told it "trust sparse on this
one," but because a rank-1 finish from either retriever contributes
more than any lower finish from the other. No `alpha` was chosen, no
score was normalized, and both of Lesson 6's misses (this one, and the
"ridges" paraphrase sparse missed) are fixed simultaneously.

## Checkpoint

- **Reciprocal Rank Fusion**: combine rankings using only position (rank
  1, 2, 3...), never raw scores, no normalization step needed.
- **`k`**: the RRF constant, controls how sharply rank 1 is favored over
  lower ranks. Tuned explicitly in Lesson 11.
- RRF isn't "better math" than Lesson 7's weighted sum, it's a
  differently-shaped fix that removes an entire failure mode (picking
  the wrong `alpha`) rather than making that failure mode smaller.

If anything here still feels unclear, ask before moving to Lesson 9.
