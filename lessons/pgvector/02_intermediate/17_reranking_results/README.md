# Lesson 17: Reciprocal rank fusion, combining rankings without tuning weights

## Where we left off

Lesson 16's hybrid score picked arbitrary weights, `0.5` for vector
similarity, `0.5` for text rank, and *added* two numbers that don't
naturally live on the same scale (cosine similarity is bounded 0 to 1;
`ts_rank` isn't bounded at all, and depends on document length and term
frequency). That works, but it's fragile: change the dataset, and the
right weights change with it. **Reciprocal rank fusion (RRF)** sidesteps
the whole problem by ignoring the raw scores entirely, and combining
only each result's *rank position*.

## The formula

For a document that appears at rank `r` in some ranked list (1st,
2nd, 3rd, ...):

```
rrf_score = 1 / (k + r)
```

`k` is a small constant (60 is the conventional default, from the
original RRF paper) that softens the effect of rank 1 versus rank 2,
without it, the single top result in any list would dominate
disproportionately. A document's *final* score is the sum of this
value across every ranked list it appears in:

```python
def reciprocal_rank_fusion(*rankings: list[str], k: int = 60) -> dict[str, float]:
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1 / (k + rank)
    return scores
```

A document ranked 1st in the vector search *and* 3rd in the keyword
search scores higher than one ranked 1st in only one of them, appearing
near the top of multiple independent rankings is itself good evidence
of relevance, exactly the intuition hybrid search is reaching for.

## Why this is more robust than Lesson 16's weighted sum

No unit conversion, no arbitrary `0.5`/`0.5` split to justify, and it
generalizes cleanly to combining *more* than two rankings later (a
reranking model's score, a recency signal, anything expressible as an
ordered list), each one just contributes its own `1 / (k + rank)` term.
The tradeoff: it only sees *rank order*, not *how much* better one
result was than the next, sometimes the raw scores really do carry
useful signal, and Lesson 16's approach (or a learned reranker, outside
this course's scope) captures that where RRF can't.

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/02_intermediate/17_reranking_results/lesson.py
```

## Checkpoint

- **reciprocal rank fusion**: `sum(1 / (k + rank))` across each ranked
  list a document appears in, combines rankings without needing
  comparable score scales.
- `k` (conventionally 60) softens how much rank 1 dominates over
  rank 2.
- Trade-off versus Lesson 16's weighted sum: more robust to scale
  differences, but blind to *how much* better one result was.

If anything here still feels unclear, ask before moving to Lesson 18.
