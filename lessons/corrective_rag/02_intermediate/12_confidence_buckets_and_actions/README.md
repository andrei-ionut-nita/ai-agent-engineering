# Lesson 12: Confidence Buckets and Actions

## Where we left off

Lesson 3 graded chunks relevant / not-relevant, a deliberate
simplification named back in Lesson 1. Lessons 10-11 built the piece
that simplification was waiting on, strip-level refinement, somewhere
useful for a middle "it's related but doesn't quite answer this" grade
to send a chunk. This lesson makes the upgrade: Yan et al. 2024's real
three-way grade, correct / ambiguous / incorrect, each mapped to its own
action.

## Three grades, three actions

- **correct**: the passage explicitly states the answer. Action: refine
  (Lesson 11) and keep the result.
- **ambiguous**: the passage is on the same topic but doesn't explicitly
  answer the question. Action: refine and keep whatever survives *and*
  flag this question as a candidate for rewriting (Lessons 6-7), the
  grader itself wasn't confident, so a differently-worded retry might
  turn up something better.
- **incorrect**: the passage has nothing useful for this question.
  Action: discard (Lesson 5).

## A parsing trap worth knowing about

```python
for bucket in ("incorrect", "ambiguous", "correct"):
    if bucket in grade:
        return bucket
```

Order matters here: the word `"correct"` is a literal substring of
`"incorrect"`. Checking `"correct"` before `"incorrect"` would
misclassify every genuinely-incorrect grade as correct, silently. This
is a real bug this lesson's own first draft hit, worth knowing about if
you ever build a grader with overlapping label names.

## The code, piece by piece

```python
AMBIGUOUS_PASSAGE = (
    "The most failure-prone part of the whole setup has been the wind "
    "speed sensor, which occasionally needs attention from time to time."
)
```

A constructed passage, not a fixture file verbatim, close in vocabulary
to the real answer in `weather-station.md`, but deliberately missing the
specific "every few months" schedule. It's on-topic (same sensor, same
project) without being a direct answer, exactly the case "ambiguous"
exists for.

```python
def act_on_grade(question: str, source: str, chunk_text: str, grade: str) -> str:
    if grade == "correct":
        return f"refine and keep -> {refine(question, chunk_text)!r}"
    if grade == "ambiguous":
        refined = refine(question, chunk_text)
        note = refined if refined else "(nothing survived refinement)"
        return f"refine, keep, AND flag for a possible query rewrite -> {note!r}"
    return "discard entirely"
```

Three branches, three actions, matching the bullets above.

## Running it

```bash
uv run python lessons/corrective_rag/02_intermediate/12_confidence_buckets_and_actions/lesson.py
```

## Expected output

```
Q: How often does the wind speed sensor need re-oiling?

weather-station.md: correct
  action: refine and keep -> 'The most failure-prone part of the whole setup has been the wind speed sensor: its bearings need re-oiling every few months, or the readings start drifting low.'

(constructed, ambiguous): ambiguous
  action: refine, keep, AND flag for a possible query rewrite -> '(nothing survived refinement)'

bookshelf.md: incorrect
  action: discard entirely
```

The ambiguous passage's refinement can come back empty, that's not a
bug. Strip-level binary grading (Lesson 10) is a stricter bar than the
chunk-level "ambiguous" grade: a passage can be topically close enough
to earn "ambiguous" at the whole-passage level while still not
containing any single sentence that, on its own, clears the "does this
sentence answer the question" bar. When that happens, the flag for a
possible rewrite is the only thing this chunk actually contributed,
which is itself useful information, it's a real signal this chunk
alone isn't enough.

## Checkpoint

- **Three-way confidence grading**: correct / ambiguous / incorrect,
  the paper's real grade, replacing Lesson 3's binary version now that
  refinement (Lessons 10-11) gives "ambiguous" a real action.
- Substring bugs are easy to introduce when label names overlap
  ("correct" inside "incorrect"), check the more specific or longer
  labels first.
- An "ambiguous" grade can still refine down to nothing, that's a
  legitimate outcome, not a contradiction, and it's exactly the signal
  that should trigger a rewrite attempt.

If anything here still feels unclear, ask before moving to Lesson 13.
