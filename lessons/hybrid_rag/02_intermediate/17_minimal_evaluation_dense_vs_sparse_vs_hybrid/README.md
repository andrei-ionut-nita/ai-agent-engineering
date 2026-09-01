# Lesson 17: Minimal Evaluation, Dense vs. Sparse vs. Hybrid

## Where we left off

Every retrieval mode this course built, dense, sparse, hybrid, gets
compared here, side by side, precision@1 on one shared labeled question
set. Before reading the numbers below, read `naive_rag` Lesson 17's
["Why this doesn't generalize (yet)"](../../../naive_rag/02_intermediate/17_minimal_evaluation_precision_at_k/README.md#why-this-doesnt-generalize-yet)
section if you haven't already, it covers exactly what a score like this
can and can't tell you, and this lesson doesn't repeat that ground.

## The code, piece by piece

```python
LABELED_QUESTIONS = [
    ("20240115", "home_network.md"),
    ...
    ("What change finally made things work reliably again?", "old_travel_router.md"),
]
```

Eleven questions: the same ten from Lessons 6-9 and 11, plus Lesson 16's
known-hard case, included deliberately. Leaving it out would have made
hybrid retrieval look flawless, which would misrepresent Lesson 16's own
finding.

```python
dense_ok = dense[0] == expected
sparse_ok = sparse[0] == expected
hybrid_ok = fused[0] == expected
```

Three separate precision@1 scores from the exact same eleven questions
and the exact same underlying rankings, so the comparison is as
apples-to-apples as this course's tools allow.

## Running it

```bash
uv run python lessons/hybrid_rag/02_intermediate/17_minimal_evaluation_dense_vs_sparse_vs_hybrid/lesson.py
```

## Expected output

```
question                                                          dense  sparse hybrid
20240115                                                          MISS   HIT    HIT
...
What change finally made things work reliably again?              MISS   MISS   MISS

precision@1, dense-only:  9/11
precision@1, sparse-only: 9/11
precision@1, hybrid RRF:  10/11
```

Hybrid beats both individual retrievers, 10/11 against 9/11 each, and
it beats them for the *reason this course exists*: it recovers dense's
one miss (the bare ID) using sparse's ranking, and recovers sparse's one
miss (the paraphrase) using dense's ranking, the two Lesson 6 originally
found. It does not recover Lesson 16's case, because neither retriever
had signal to fuse there in the first place, RRF only redistributes
what's already present, it doesn't add information neither ranking
found.

With eleven questions, "9/11 vs 10/11" is one question's difference, not
a result you'd stake much on in isolation, naive_rag Lesson 17's caveat
about small samples applies exactly as much here. What makes this result
worth reporting anyway isn't the precision of the number, it's that the
*specific* question hybrid recovers is exactly the one this course
predicted it would, and the *specific* question it still misses is
exactly the one Lesson 16 already explained why fusion can't reach. The
score corroborates a mechanism this course already demonstrated
piece by piece, it isn't standing in for that demonstration on its own.

## Checkpoint

- Hybrid retrieval scores strictly higher than either retriever alone on
  this course's labeled set, and the specific question it recovers
  matches the specific blind spots demonstrated all the way back in
  Lesson 6.
- It doesn't recover Lesson 16's failure case, confirming that fusion
  redistributes existing signal rather than creating new signal.
- Eleven questions is enough to illustrate the mechanism, not enough to
  trust the exact numbers, the same caveat `naive_rag` Lesson 17 raised
  applies here without modification.

If anything here still feels unclear, ask before moving to Lesson 18.
