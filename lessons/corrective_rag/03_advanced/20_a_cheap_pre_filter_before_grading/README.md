# Lesson 20: A Cheap Pre-Filter Before Grading

## Where we left off

Lesson 19 put a real number on grading's cost: one model call per chunk
(or per strip), scaling with `k`. One easy win is grading fewer chunks
in the first place, without giving up any judgment quality on the ones
that matter. This lesson adds a **similarity-score pre-filter**: a cheap
threshold check, entirely local (no model call), that runs before the
LLM grader even sees a chunk.

## A pre-filter, not a replacement

This is not `naive_rag` Lesson 14's threshold repurposed to make final
decisions, it's a much looser version of the same idea, used only to
rule out chunks that are obviously, cheaply, unrelated by score alone.
Anything that clears the bar still goes through the real LLM grader
(Lessons 3, 12), the pre-filter's only job is skipping grading calls
that would almost certainly come back "not relevant" anyway.

## The code, piece by piece

```python
PRE_FILTER_MIN_SCORE = 0.55
```

Chosen the same way `naive_rag` Lesson 14's threshold was: just above
the observed "unrelated sentence" baseline, not from a formula. Kept
loose on purpose, a pre-filter that's too aggressive risks dropping a
chunk grading would have correctly kept, which defeats the entire point
of adding grading in the first place.

```python
with_prefilter = [c for c in all_scored if c["score"] >= PRE_FILTER_MIN_SCORE]
...
grades = {c["source"]: grade_chunk(question, c["text"]) for c in with_prefilter}
```

Only chunks that clear the pre-filter get an actual grading call. The
ones that don't are treated as not-relevant without ever calling the
model, saving exactly the calls Lesson 19 showed add up.

## Running it

```bash
uv run python lessons/corrective_rag/03_advanced/20_a_cheap_pre_filter_before_grading/lesson.py
```

## Expected output

```
Q: Project Aurora's Raspberry Pi writes sensor readings to a SQLite file on its SD card. Where does that Raspberry Pi physically live in the house?

All 5 chunks, scored (no grading yet):
  weather-station.md: score=0.7xxx
  bookshelf.md: score=0.7xxx
  cello-practice.md: score=0.5xxx
  garden.md: score=0.5xxx
  pizza-dough.md: score=0.51xx

Without pre-filter: 5 chunk(s) would need LLM grading
With pre-filter (score >= 0.55): 4 chunk(s) need LLM grading
  ['weather-station.md', 'bookshelf.md', 'cello-practice.md', 'garden.md']

1 grading call(s) skipped entirely, at zero risk to this course's running example:
  weather-station.md: not_relevant
  bookshelf.md: relevant
  cello-practice.md: relevant
  garden.md: not_relevant
```

On this course's five-document corpus the saving is small (one call),
the point is the mechanism: at real scale, with hundreds or thousands
of candidates per query, a loose local pre-filter routinely rules out
the majority of chunks before a single grading call is spent on them.

## Checkpoint

- A pre-filter trades a small amount of recall risk (a genuinely
  relevant chunk scoring just under the bar) for a real reduction in
  grading calls, kept loose specifically to make that risk small.
- This is one of two direct responses to Lesson 19's cost problem, the
  other being Lesson 13's caching, both apply at once in a real system.
- The LLM grader still makes every real relevance decision, the
  pre-filter only decides which chunks are cheap enough to skip
  entirely.

If anything here still feels unclear, ask before moving to Lesson 21.
