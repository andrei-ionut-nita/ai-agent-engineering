# Lesson 7: Re-Retrieval With the Rewritten Query

## Where we left off

Lesson 6 built `rewrite_query()` and showed it honestly declining to
change a question that had no wording problem to fix (France still
isn't in the corpus, no matter how it's asked). This lesson closes the
loop on the case rewriting *is* meant for: a question phrased in words
that don't match the corpus, where the answer is genuinely there.

## A genuine wording miss, this time

`"The roof whirligig, how often does it need love?"` is slangy enough
that naive top-1 retrieval reaches for `garden.md` (something about the
outdoors, scored highest, but wrong), while the actual answer, the wind
speed sensor's re-oiling schedule, sits in `weather-station.md`. Grading
correctly flags the top-1 miss; the fix here isn't filtering (there's
nothing else in a `k=1` retrieval to fall back to), it's asking the
question better.

## The code, piece by piece

```python
original_top1 = retrieve(QUESTION, store, k=1)[0]
original_grade = grade_chunk(QUESTION, original_top1["text"])
```

Naive retrieval and grading, unchanged from earlier lessons, at `k=1`
specifically so there's no over-fetched fallback chunk to filter down
to, this case has to be fixed by changing the query, not by picking a
different already-retrieved chunk.

```python
new_top1 = retrieve(rewritten, store, k=1)[0]
new_grade = grade_chunk(rewritten, new_top1["text"])
```

The re-retrieval itself: Lesson 2's exact `retrieve()` function, called
a second time, with the rewritten string in place of the original
question. Nothing about *how* retrieval works changed, only what it was
asked. That's the core idea of this whole simplification: correction
happens by changing the input to an unchanged retrieval step, not by
making retrieval itself smarter.

## Running it

```bash
uv run python lessons/corrective_rag/01_beginner/07_re_retrieval_with_the_rewritten_query/lesson.py
```

## Expected output

```
Q: 'The roof whirligig, how often does it need love?'
Naive top-1: garden.md (score=0.5xxx) -> not_relevant

Rewritten query: '<a clearer version, mentioning the weather station and its anemometer/sensor>'
Re-retrieved top-1: weather-station.md (score=0.6xxx) -> relevant

The rewrite changed which chunk retrieval found, and the new chunk grades relevant. ...
```

The rewritten query's exact wording varies between runs, but it should
consistently mention the weather station or its wind sensor by name,
and re-retrieval should consistently land on `weather-station.md`,
graded relevant.

## Checkpoint

- **Re-retrieval**: the same retrieval function, called again with a
  different query string, no new retrieval logic needed.
- Rewriting fixes vocabulary mismatches between the question and the
  corpus, this lesson's success case, and Lesson 6's honest failure
  case (a genuine knowledge gap) are the two outcomes you'll see in
  practice, and they need different fixes: rewriting for the first,
  external search (Lesson 22) for the second.
- Lesson 8 assembles Lessons 2-7 into one pipeline: retrieve, grade,
  filter or rewrite depending on what grading found, re-retrieve if
  needed, generate.

If anything here still feels unclear, ask before moving to Lesson 8.
