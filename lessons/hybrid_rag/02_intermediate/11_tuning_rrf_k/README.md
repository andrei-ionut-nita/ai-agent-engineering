# Lesson 11: Tuning RRF's k

## Where we left off

Lesson 8 introduced RRF's constant `k` (60, the standard default) without
explaining what changing it actually does. This lesson does two things:
shows `k`'s real effect on a fused ranking, using a synthetic example
where dense and sparse genuinely disagree, then sweeps `k` on this
course's own ten labeled questions, and is explicit about a trap that
sweep falls straight into.

## The code, piece by piece

```python
synthetic_dense = ["X", "Y", "P", "Q", "R", "S"]   # X is #1, dead last in sparse
synthetic_sparse = ["P", "Q", "Y", "R", "S", "X"]  # Y is #3 in both, consistent
```

`X` gets a spectacular rank-1 finish in one ranking and a terrible one
in the other. `Y` never wins outright, but never does badly either. This
is the case `k` actually controls: does one great finish outweigh one
terrible one, or does consistent-but-unspectacular win out?

## Running it

```bash
uv run python lessons/hybrid_rag/02_intermediate/11_tuning_rrf_k/lesson.py
```

## Expected output

```
Synthetic example, two rankings that disagree on X and Y:
  dense:  ['X', 'Y', 'P', 'Q', 'R', 'S']   (X is #1, but dead last in sparse)
  sparse: ['P', 'Q', 'Y', 'R', 'S', 'X']   (Y is #3 in both, more consistent)
  k=1     fused order: ['P', 'X', 'Y', 'Q', 'R', 'S']
  k=60    fused order: ['P', 'Y', 'Q', 'X', 'R', 'S']
  k=1000  fused order: ['P', 'Y', 'Q', 'X', 'R', 'S']
```

At `k=1`, `X` outranks `Y`, one spectacular finish is worth more than
one consistent showing. By `k=60` (this course's default since Lesson
8), that stops holding, `X` drops behind both `Y` and `Q`, consistency
starts winning. Small `k` rewards a strong opinion from either
retriever; large `k` rewards broad, if unspectacular, agreement between
them.

```
     k   hits/10
     1      10/10
     5      10/10
   ...
  1000      10/10
```

Every value of `k` from 1 to 1000 scores 10/10 on this course's own ten
questions. Not "roughly the same," identical. This is Lesson 7's
fragility point taken further: this course's labeled set is small enough
that it can't even *see* `k`'s effect, let alone tell a good value from
a bad one, the flat sweep above isn't evidence `k` doesn't matter, it's
evidence this particular eval set has no power to detect that it does.

## Why this lesson is the contaminated case, on purpose

The README convention set for this series (`docs/RAG-SERIES-PLAN/README.md`)
flags exactly this: tuning a hyperparameter against the same labeled set
you later report a score on invalidates that score. This lesson does
precisely that, sweeping `k` against the same ten questions Lesson 17
scores hybrid retrieval on, deliberately, so you see the trap from the
inside rather than being told about it in the abstract. A real pipeline
keeps a tuning set and a reporting set separate, or, more honestly at
this scale, just keeps `k` at its standard default (`60`) and doesn't
pretend five or ten questions can respectably tune anything.

## Checkpoint

- **`k`**: small values let one strong finish in either ranking dominate;
  large values reward broad agreement between both rankings instead.
- A hyperparameter sweep that can't even move the score on your eval set
  is telling you the eval set is too small to tune with, not that the
  hyperparameter doesn't matter.
- This lesson deliberately tuned against the same set Lesson 17 reports
  a score on. Notice it, don't repeat it in a real system.

If anything here still feels unclear, ask before moving to Lesson 12.
