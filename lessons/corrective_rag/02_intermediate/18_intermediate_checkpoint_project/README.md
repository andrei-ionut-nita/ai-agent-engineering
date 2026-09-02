# Lesson 18: Intermediate Checkpoint - Notes Search With a "Corrected" Indicator

## What this is

No new concepts in this lesson. This is a checkpoint: a small, real
script built entirely out of ideas from Lessons 10 through 17, combined
into one thing. If you can read `lesson.py` and understand why every
piece is there, you've mastered the Intermediate tier. If any piece
feels unfamiliar, that's a sign to revisit the lesson it came from
before continuing to Advanced.

## What it does

Loads all five fixture notes, then answers questions through `ask()`:
retrieve, three-way confidence grade (Lesson 12), refine at the strip
level (Lessons 10-11), rewrite and re-retrieve if nothing survives
(Lessons 6-7), generate with source citations, and print whether
correction actually changed anything, the same visible indicator idea
from Lesson 9's Beginner checkpoint, now backed by the more precise
Intermediate-tier machinery instead of binary grading.

## Where each piece came from

```python
graded = [{**c, "confidence": grade_confidence(query, c["text"])} for c in retrieved]
kept = [c for c in graded if c["confidence"] in ("correct", "ambiguous")]
```

Lesson 12's three-way grade and action mapping: both "correct" and
"ambiguous" chunks are kept (and refined below), only "incorrect" is
dropped outright.

```python
context = "\n\n".join(f"[{c['source']}]\n{refine(effective_query, c['text'])}" for c in kept)
```

Lesson 11's `refine()`, applied to every kept chunk before it reaches
the prompt, and Lesson 15's citation format (`[source.md]`), combined
into one context string.

```python
used_sources = {c["source"] for c in kept}
corrected = naive_top1_source is not None and naive_top1_source not in used_sources
```

Lesson 9's correction indicator, unchanged in spirit: compare what
naive top-1 alone would have used against what the full pipeline
actually used.

## Running it

```bash
uv run python lessons/corrective_rag/02_intermediate/18_intermediate_checkpoint_project/lesson.py
```

## Expected output

```
Loaded and embedded 5 notes from .../fixtures/notes

Q: Project Aurora's Raspberry Pi writes sensor readings to a SQLite file on its SD card. Where does that Raspberry Pi physically live in the house?
  [retrieval was corrected]
A: Based on the provided context, Project Aurora's Raspberry Pi lives on a small shelf next to the bookshelf in the study [bookshelf.md].

Q: What's the cold ferment time for the pizza dough?
  [no correction needed]
A: The cold ferment time for the pizza dough is 48 hours [pizza-dough.md].
```

## Try this yourself

Without looking anything up:

- Ask Lesson 16's exact question ("How often does Project Aurora's wind
  speed sensor need re-oiling?") through `ask()`. Does the citation
  correctly point at `weather-station.md`? Would this pipeline have any
  way to notice if `weather-station.md`'s content had been subtly wrong,
  the way Lesson 16's fabricated passage was?
- Trace through what happens if every retrieved chunk grades
  "incorrect": which branch of `ask()` runs, and what does the final
  indicator print?
- Compare this lesson's citation style to `naive_rag` Lesson 25's
  capstone. Both use `[source.md]`, on purpose, matching conventions
  across this series makes a future course able to reuse either one's
  prompt template without translation.

If you can make these changes confidently, you're ready for the
Advanced tier, starting at Lesson 19.
