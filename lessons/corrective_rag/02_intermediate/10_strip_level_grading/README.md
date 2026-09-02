# Lesson 10: Strip-Level Grading

## Where we left off

Beginner-tier grading (Lesson 3) judged a whole chunk at once: relevant
or not. That's coarse. `weather-station.md` is eight sentences about a
weather station project, only one of which actually answers "how often
does the wind speed sensor need re-oiling?" A whole-chunk grade has no
way to say "mostly not relevant, except this one part." Yan et al.
2024's paper solves this with **strips**: splitting a chunk into
fine-grained pieces (sentences, in this course) and grading each one
individually.

## Why this matters, not just "more precise"

Strip-level grading is what makes the paper's "correct" action
(knowledge refinement) possible at all. A whole chunk graded "relevant"
still hands generation seven sentences of noise alongside the one that
matters, wasting context and giving the model more room to blend in
irrelevant details. Grading at the strip level identifies *exactly*
which sentences earn their place, setting up Lesson 11's recomposition:
keeping only the relevant strips instead of the whole chunk.

## The code, piece by piece

```python
def split_into_strips(text: str) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    strips = []
    for paragraph in paragraphs:
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        strips.extend(s.strip() for s in sentences if s.strip())
    return strips
```

A strip, here, is one sentence. Splitting on paragraph breaks first,
then sentences within each paragraph, is crude (no handling for
abbreviations like "Dr." or decimal numbers), fine for this course's
short, plain fixture notes, and, like Lesson 3's cosine similarity, kept
simple on purpose so nothing about how the split works is hidden.

```python
def grade_strip(question: str, strip: str) -> str:
    prompt = GRADE_PROMPT.format(question=question, sentence=strip)
    ...
```

The same binary grading call from Lesson 3, unchanged, just run once per
strip instead of once per chunk. Grading logic doesn't change between
whole-chunk and strip-level, only what gets handed to it does.

## Running it

```bash
uv run python lessons/corrective_rag/02_intermediate/10_strip_level_grading/lesson.py
```

## Expected output

```
Q: How often does the wind speed sensor need re-oiling?

weather-station.md split into 8 strips:

  [1] (not_relevant) # Project Aurora
  [2] (not_relevant) Project Aurora is a personal weather station...
  ...
  [8] (relevant) The most failure-prone part of the whole setup has been the wind speed
sensor: its bearings need re-oiling every few months, or the readings
start drifting low.

1/8 strips graded relevant. ...
```

Exactly one of the eight strips (the sentence that actually names the
re-oiling schedule) should grade relevant, consistently, since it's the
only sentence in the note that answers this specific question.

## Checkpoint

- **strip**: a fine-grained piece of a chunk (here, one sentence), the
  unit the paper's real grading operates on, once whole-chunk grading
  isn't precise enough.
- Strip-level grading doesn't replace chunk-level retrieval, chunks are
  still what gets retrieved by similarity, strips are what gets graded
  and kept *within* an already-retrieved chunk.
- This is what makes Lesson 11's recomposition (keeping only relevant
  strips) and Lesson 12's three-way confidence grade (which needs
  strip-level granularity to act on "ambiguous" chunks) possible.

If anything here still feels unclear, ask before moving to Lesson 11.
