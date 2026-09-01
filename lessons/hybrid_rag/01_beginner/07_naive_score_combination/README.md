# Lesson 7: Naive Score Combination

## Where we left off

Lesson 6 showed dense and sparse retrieval failing in different places,
on the same corpus, at the same overall accuracy. The obvious next move:
combine their scores into one ranking. This lesson does that the most
direct way possible, a weighted sum, and shows why picking the weight is
harder than it looks.

## The code, piece by piece

```python
def min_max_normalize(scores: dict[str, float]) -> dict[str, float]:
    low, high = min(values), max(values)
    return {name: (score - low) / spread for name, score in scores.items()}
```

Dense scores already live in `[0, 1]` (cosine similarity), but BM25
scores are unbounded, could be `0.0`, could be `12.4`. Min-max squashes
both onto the same `[0, 1]` range, per query, before they get combined,
otherwise whichever retriever happens to produce larger raw numbers
would dominate the sum regardless of which is actually more relevant.

```python
combined = {name: alpha * dense_norm[name] + (1 - alpha) * sparse_norm[name] for name in names}
```

`alpha` controls the blend: `1.0` is pure dense, `0.0` is pure sparse,
`0.5` is an even split. This lesson sweeps `alpha` across the full range
and checks accuracy on all ten of Lesson 6's questions at each value.

## Running it

```bash
uv run python lessons/hybrid_rag/01_beginner/07_naive_score_combination/lesson.py
```

## Expected output

```
  alpha   lexical hits   semantic hits   total
    0.0              5/5              4/5     9/10
    0.2              5/5              5/5    10/10
    0.4              5/5              5/5    10/10
    0.5              5/5              5/5    10/10
    0.6              5/5              5/5    10/10
    0.8              5/5              5/5    10/10
    1.0              4/5              5/5     9/10
```

Every blended value between the two pure extremes hits 10/10, fixing
both Lesson 6 misses at once. That looks like a solved problem, but look
at how this number was found: by trying every `alpha` from 0.0 to 1.0
and checking each one against an answer key we already had. That's the
same tune-on-your-eval-set trap `naive_rag` Lesson 17 warned about,
except here it's a single number (`alpha`) instead of a whole strategy,
and in a real system you don't have a labeled answer key sitting around
to sweep against for every new kind of question that shows up.

The plateau is also wide here specifically because this corpus is small
and each retriever already scores 9/10 alone, there's a lot of room for
"good enough" blends to land inside it by accident. A corpus where dense
and sparse are more evenly matched, or a question mix skewed more
lexical or more semantic than this one, would narrow that safe range,
possibly to nothing, and you'd have no way to know in advance which
`alpha` is safe without, again, a labeled set to check against.

## Checkpoint

- **Min-max normalization**: squash unbounded sparse scores and bounded
  dense scores onto the same `[0, 1]` range before combining them.
- **`alpha`**: the blend weight between dense and sparse, tuned by
  sweeping values against a labeled question set, the same fragile
  pattern flagged for hyperparameter tuning generally.
- The weight that works depends on the query mix you tuned it against,
  which you don't know in advance and can't fully anticipate. Lesson 8
  introduces a fusion method that doesn't require picking a weight at
  all.

If anything here still feels unclear, ask before moving to Lesson 8.
