# Lesson 17: Minimal Evaluation, Before vs. After Correction

## Where we left off

Every earlier lesson judged correction by eyeballing one or two
questions. This lesson replaces eyeballing with `naive_rag` Lesson 17's
**precision@k**, scored twice, once with plain naive retrieval, once
with this course's grade-and-filter correction, so the improvement is a
number, not an impression. It also adds a check `naive_rag` Lesson 17
never needed: does the *generated answer* actually get better, not just
the retrieval metric.

This lesson assumes you've read `naive_rag`'s
[Lesson 17 README](../../../naive_rag/02_intermediate/17_minimal_evaluation_precision_at_k/README.md),
specifically its **"Why this doesn't generalize (yet)"** section, rather
than re-deriving it here. Everything that section says about five
questions being too few to trust the exact number, and about the
tune/eval contamination trap, applies here without modification.

## The labeled set

```python
LABELED_QUESTIONS = [
    ("Project Aurora's Raspberry Pi writes sensor readings...", "bookshelf.md"),
    ("How often does the wind speed sensor need re-oiling?", "weather-station.md"),
    ("What's the cold ferment time for the pizza dough?", "pizza-dough.md"),
    ("What piece is being practiced on the cello?", "cello-practice.md"),
    ("Which vegetables grow in the second raised bed?", "garden.md"),
]
```

Four of these five are unambiguous, `naive_rag`-style questions, naive
retrieval already handles them correctly, they exist so the score isn't
measuring a single question's fluke. The first is this course's own
running example, the one question this whole labeled set actually
depends on to demonstrate anything: naive top-1 retrieval confidently
returns the wrong source for it (Lesson 2).

## The code, piece by piece

```python
def precision_before(store, query_vectors) -> float:
    for ...:
        top1 = retrieve_by_vector(qv, store, k=1)[0]
        hit = top1["source"] == expected_source
```

Plain naive retrieval, `k=1`, no grading, the `naive_rag` baseline.

```python
def precision_after(store, query_vectors) -> float:
    for ...:
        top3 = retrieve_by_vector(qv, store, k=3)
        relevant_sources = [c["source"] for c in top3 if grade_chunk(question, c["text"]) == "relevant"]
        hit = expected_source in relevant_sources
```

Correction, exactly Lessons 4-5's pipeline: over-fetch, grade every
candidate, keep what's relevant, check whether the expected source
survived. Nothing new, this lesson just runs it across five questions
instead of one and scores the result.

```python
naive_answer = generate_answer(hard_question, naive_top1)
corrected_answer = generate_answer(hard_question, corrected_chunks)
```

The answer-quality check: generate from naive retrieval's context and
from correction's context, on the one question where they differ, and
compare the actual text. Precision@k alone doesn't prove this course's
Lesson 1 premise, "retrieval was more precise" isn't the same claim as
"the user got a better answer," this check closes that gap directly,
per this course's To-Do List commitment.

## Running it

```bash
uv run python lessons/corrective_rag/02_intermediate/17_minimal_evaluation_before_vs_after_correction/lesson.py
```

## Expected output

```
precision@1, BEFORE correction (naive top-1 only):
  [MISS] "Project Aurora's Raspberry Pi..." -> expected bookshelf.md, got weather-station.md
  [HIT ] 'How often does the wind speed sensor need re-oiling?' -> expected weather-station.md, got weather-station.md
  [HIT ] "What's the cold ferment time for the pizza dough?" -> expected pizza-dough.md, got pizza-dough.md
  [HIT ] 'What piece is being practiced on the cello?' -> expected cello-practice.md, got cello-practice.md
  [HIT ] 'Which vegetables grow in the second raised bed?' -> expected garden.md, got garden.md
  Score: 0.80 (4/5)

precision@1-equivalent, AFTER correction (over-fetch k=3, grade, filter):
  [HIT ] "Project Aurora's Raspberry Pi..." -> expected bookshelf.md, got ['bookshelf.md', ...]
  [HIT ] ... (all five hit)
  Score: 1.00 (5/5)

Answer quality check on: "Project Aurora's Raspberry Pi..."
  Naive answer:     The provided context does not contain the answer to where the Raspberry Pi physically lives in the house.
  Corrected answer: Based on the provided context, Project Aurora's Raspberry Pi lives on a small shelf next to the bookshelf in the study...
```

Precision@1 goes from 0.80 to 1.00, entirely on the strength of this
course's one hard question, and the generated answer visibly changes
from a hedge to a real, grounded answer. That's this course's premise,
both halves of it: retrieval got measurably better, and the thing a user
actually reads got measurably better too.

## Checkpoint

- Precision@k, scored before and after correction, turns "did grading
  and filtering help?" into a number you can compare, the same idea
  `naive_rag` Lesson 17 introduced, applied here to a before/after
  comparison instead of a single snapshot.
- A retrieval-precision improvement doesn't automatically mean a
  generation-quality improvement, Lesson 16 already showed grading can
  share the generator's blind spots, this lesson's answer-quality check
  is what actually confirms the user-facing outcome improved, not just
  the metric.
- Every caveat in `naive_rag` Lesson 17's "Why this doesn't generalize
  (yet)" section still applies: five questions is enough to demonstrate
  the mechanism, not enough to trust the exact number, and this course's
  own Lesson 14 rewrite-strategy heuristic was deliberately tuned
  against a different signal than this lesson's score, not against it.

If anything here still feels unclear, ask before moving to Lesson 18.
