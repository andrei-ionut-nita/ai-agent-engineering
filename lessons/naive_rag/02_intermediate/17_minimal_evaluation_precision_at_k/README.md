# Lesson 17: Minimal Evaluation, Precision@k

## Where we left off

Every lesson so far judged retrieval by eyeballing one or two questions
and deciding "yes, that looks right." That doesn't scale, and it doesn't
survive a change (a new chunking strategy, a different `k`) without
re-eyeballing everything by hand again. This lesson replaces eyeballing
with a small, repeatable score: **precision@k**.

## What precision@k actually measures

Given a set of questions where you (a human) already know the correct
source for each one, **precision@k** asks: for what fraction of those
questions does the correct source appear somewhere in the top `k`
retrieved results? A precision@1 of 1.0 means every question's correct
source was retrieval's single best guess; 0.6 means 60% of the time it
was.

This requires a **labeled evaluation set**, questions paired with known-
correct answers, prepared by a human ahead of time:

```python
LABELED_QUESTIONS = [
    ("How often does the wind speed sensor need re-oiling?", "weather-station.md"),
    ...
]
```

There's no way around this step, evaluation needs ground truth to
compare against; it's exactly the same idea as Lesson 15's citations,
just applied to grade retrieval itself instead of grading an answer.

## The code, piece by piece

```python
questions = [question for question, _ in LABELED_QUESTIONS]
query_vectors = embed_texts(questions)
```

Every question in the labeled set is embedded once, in a single batch
call, up front, the same batching idea from Lesson 5, applied here for
the same reason: five separate embedding calls per `k` value (ten total,
across `k=1` and `k=2`) would burn through the free tier's
requests-per-minute limit far faster than five questions actually need
to.

```python
for (question, expected_source), query_vector in zip(LABELED_QUESTIONS, query_vectors):
    retrieved = retrieve_by_vector(query_vector, store, k)
    retrieved_sources = [r["source"] for r in retrieved]
    hit = expected_source in retrieved_sources
    hits += hit
```

For each labeled question (paired with its already-computed vector),
retrieve the top `k` chunks, check whether the expected source appears
anywhere among them (not just as the single top result, "in the top `k`"
is the whole point of the metric), and count it as a hit or miss.
`hits += hit` works because `True`/`False` behave as `1`/`0` in
arithmetic in Python.

```python
return hits / len(LABELED_QUESTIONS)
```

The final score: fraction of questions where retrieval succeeded, a
single number you can watch go up or down as you change chunking,
`k`, or the embedding model.

## Running it

```bash
uv run python lessons/naive_rag/02_intermediate/17_minimal_evaluation_precision_at_k/lesson.py
```

## Expected output

```
precision@1:
  [HIT ] 'How often does the wind speed sensor need re-oiling?' -> expected weather-station.md, got ['weather-station.md']
  [HIT ] "What's the cold ferment time for the pizza dough?" -> expected pizza-dough.md, got ['pizza-dough.md']
  [HIT ] 'How is the bookshelf organized?' -> expected bookshelf.md, got ['bookshelf.md']
  [HIT ] 'What piece is being practiced on the cello?' -> expected cello-practice.md, got ['cello-practice.md']
  [HIT ] 'Which vegetables grow in the second raised bed?' -> expected garden.md, got ['garden.md']
  Score: 1.00 (5/5)

precision@2:
  ...
  Score: 1.00 (5/5)
```

A perfect score here reflects the small, clean corpus this course uses,
five short documents on clearly distinct topics. Precision@k becomes far
more informative (and less likely to sit at a perfect 1.0) on a larger,
messier document collection, where some questions genuinely have
ambiguous or overlapping correct answers.

## Why this doesn't generalize (yet)

Five labeled questions is enough to demonstrate the *mechanism* of
precision@k, not enough to actually trust the number. With five
questions, one lucky or unlucky match swings the score by 20 points
(1/5), so "0.80 vs. 1.00" between two chunking strategies could just as
easily be noise as a real difference. A real evaluation set needs enough
labeled questions, usually dozens to hundreds depending on how fine a
difference you need to detect, that a single flipped answer barely moves
the score.

There's a second trap worth naming even though this lesson doesn't fall
into it: Lesson 14's similarity threshold (`0.55`) was chosen from
Lesson 3's *separate* observation of what an unrelated sentence scores,
not from this lesson's labeled set. If it had been tuned by nudging
`MIN_SCORE` until precision@k on these same five questions hit 1.00,
that score would no longer measure anything, it would just describe how
well the threshold was fit to the five questions it's also being
graded on. Tune hyperparameters against one signal; report the score
against a different, held-out one. Conflating the two is the most common
way a "the metric went up" claim turns out to be meaningless.

## Checkpoint

- **precision@k**: the fraction of labeled questions whose correct
  source appears somewhere in the top `k` retrieved results.
- **labeled evaluation set**: questions paired with a known-correct
  answer, prepared by a human, the ground truth any evaluation metric
  needs to compare against.
- A single number like this turns "does this change help retrieval?"
  from a judgment call into something you can actually compare, before
  and after.
- Small labeled sets show *how* to measure, not a trustworthy score, and
  tuning a hyperparameter against the same set you evaluate it on
  invalidates the score. Both traps get bigger, not smaller, once RRF
  weights, traversal depth, or routing rules show up later in the series.

If anything here still feels unclear, ask before moving to Lesson 18.
