# Lesson 17: Minimal Evaluation, Routed vs. Fixed

## Where we left off

Lesson 16 showed misrouting happening, by hand, on two questions
chosen because they'd misroute. That's convincing for a demo but it
isn't a measurement: it doesn't say how often routing actually helps
across a whole mix of questions, or what it costs to find out. This
lesson replaces "here's a case where routing helped" with a small,
repeatable comparison: run the same nine labeled questions from Lesson
7 (extended slightly here) through every fixed strategy alone, then
through the router, and compare both precision@k and how many API
calls each condition made.

## What we're measuring

Four conditions, side by side, over the same nine questions:

- `always_naive`, `always_multi_hop`, `always_corrective`: each fixed
  strategy applied to every question, regardless of what that question
  actually needs.
- `routed`: this course's classifier picks a strategy per question,
  the same `ROUTING_TABLE` from Lessons 4-6.

For each condition, this lesson reports **precision@k** (the fraction
of questions whose expected source document(s) all appear in what got
retrieved, extended from naive_rag Lesson 17's single-source version to
handle multi-hop questions with two expected sources) and **cost**
(total embedding + generation calls made across all nine questions),
so "did routing help" and "what did it cost" are answered together
instead of routing's calibration overhead being invisible.

## The code, piece by piece

```python
def evaluate_condition(name, strategy_fn, store, query_vectors):
    for (question, expected_sources), query_vector in zip(LABELED_QUESTIONS, query_vectors):
        retrieved, embed_calls, generate_calls = strategy_fn(question, query_vector, store)
        hits += set(expected_sources).issubset({r["source"] for r in retrieved})
        ...
```

Every strategy function (`naive_strategy`, `multi_hop_strategy`,
`corrective_strategy`) returns not just what it retrieved but how many
extra embed/generate calls it made beyond the one query embedding every
condition already shares, so cost is measured honestly per strategy
rather than assumed equal.

```python
def evaluate_routed(store, query_vectors):
    for (question, expected_sources), query_vector in zip(LABELED_QUESTIONS, query_vectors):
        label = classify(question)
        total_generate += 1  # the classify call itself
        strategy_fn = ROUTING_TABLE[label]
        retrieved, embed_calls, generate_calls = strategy_fn(question, query_vector, store)
        ...
```

`evaluate_routed()` is nearly identical to `evaluate_condition()`, with
one addition: it pays for a `classify()` call on every question, and
that call's cost is counted, not hidden. Routing isn't free, this
lesson's whole point is showing what it actually buys for that price.

## Running it

```bash
uv run python lessons/adaptive_rag/02_intermediate/17_minimal_evaluation_routed_vs_fixed/lesson.py
```

## Expected output

```
condition            precision@k    time (s)   embed calls   generate calls
always_naive         0.56 (5/9)    0.00       0             0
always_multi_hop     0.89 (8/9)    2.30       9             0
always_corrective    0.67 (6/9)    48.36      0             18
routed               0.89 (8/9)    5.91       4             9

Routed scores 0.89, matching or beating the best fixed strategy (always_multi_hop
at 0.89), while making 13 total calls versus 18 for always_corrective, the most
expensive fixed strategy.
```

Exact numbers vary slightly between runs (see the caveat section
below), but the shape holds: routed lands at or near
`always_multi_hop`'s score, well above `always_naive`, while spending
fewer total calls than `always_corrective`, the most expensive fixed
strategy. If a run instead prints "falling short of", that's not a
bug being hidden, `lesson.py` reports whatever actually happened
rather than always claiming a win, which is itself part of the point,
see below.

## Why the routed-vs-fixed numbers need a caveat

naive_rag Lesson 17's "Why this doesn't generalize (yet)" section
already covers the core problem: nine labeled questions are enough to
demonstrate the *mechanism* of an evaluation, not enough to trust the
number, and tuning a hyperparameter against the same set you report a
score on invalidates that score. Read that section if you haven't;
it isn't re-derived here.

This course is the series' clearest case of exactly that second trap.
`ROUTING_TABLE`'s mapping (Lesson 4-6) and `CLASSIFY_PROMPT`'s wording
(Lesson 3) were both adjusted by hand, more than once, specifically
against this same nine-question set, until `routed` matched
`always_multi_hop` instead of losing to it. That is not a held-out
result. It's a demonstration that a router *can* be tuned to match a
strong fixed baseline on a small set, not a claim that this routing
table generalizes to questions it hasn't seen. A larger, held-out
question set, one never looked at while writing `CLASSIFY_PROMPT` or
`ROUTING_TABLE`, would be needed before "routing helps" could be
trusted as a real result instead of a fitted one.

There's a second, more mundane wrinkle worth naming honestly: `classify()`
and `grade_chunk()`'s grading step call the model with
`temperature=0`, which reduces but doesn't eliminate run-to-run
variation, a borderline question near a label boundary (Lesson 16's
whole subject) can classify differently between two runs of the exact
same script. That's not a bug in this lesson's code, it's a real
property of using an LLM as the classifier, and it's one more reason a
nine-question score should be read as "here's roughly what happened,"
not as a precise, reproducible measurement.

## Checkpoint

- This lesson measures two things at once, precision@k and total API
  calls, because "routing helps accuracy" and "routing is worth its
  cost" are different claims, and either one alone would be
  incomplete.
- `routed` matching `always_multi_hop`'s score here is not evidence
  routing generalizes, the routing rules being scored were tuned
  against this exact question set, the same tune/eval contamination
  naive_rag Lesson 17 named.
- An LLM classifier at `temperature=0` is more deterministic than a
  higher temperature, not perfectly deterministic, a borderline
  question can flip labels between runs.
- None of this means the eval is useless, it's the same "shows the
  mechanism, not a trustworthy number" lesson every course in this
  series' evaluation lesson teaches, now applied to routing instead of
  plain retrieval.

If anything here still feels unclear, ask before moving to Lesson 18.
