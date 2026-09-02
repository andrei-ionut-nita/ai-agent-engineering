# Lesson 11: Recomposing Context From Relevant Strips

## Where we left off

Lesson 10 graded `weather-station.md`'s eight sentences individually and
found exactly one relevant. This lesson does something with that
information: instead of handing generation the whole 685-character
chunk (Beginner tier's keep-or-drop-the-whole-chunk choice), recompose a
new, shorter context out of only the strips that graded relevant. This
is the paper's **knowledge refinement**, the action taken on a chunk
graded "correct."

## Decompose, then recompose

That's the paper's own phrase for this: decompose a chunk into strips
(Lesson 10), grade each one, then recompose the ones that survived back
into a single piece of text, in their original order. It's the same
idea as Lesson 5's filtering, applied one level down, filtering
sentences within a kept chunk instead of filtering whole chunks within
a retrieved set.

## The code, piece by piece

```python
def recompose(question: str, chunk_text: str) -> str:
    strips = split_into_strips(chunk_text)
    relevant_strips = [s for s in strips if grade_strip(question, s) == "relevant"]
    return " ".join(relevant_strips)
```

Split, grade, filter, and glue back together, four ideas you've already
seen (Lessons 5 and 10), combined into one function. The result isn't a
summary or a paraphrase, it's a subset of the original sentences,
verbatim, so nothing generation reads was invented by this step.

## Running it

```bash
uv run python lessons/corrective_rag/02_intermediate/11_recomposing_context_from_relevant_strips/lesson.py
```

## Expected output

```
Q: How often does the wind speed sensor need re-oiling?

Whole chunk as context (685 chars):
  Based on the context, the wind speed sensor needs re-oiling every few months.

Recomposed context, relevant strips only (160 chars):
  'The most failure-prone part of the whole setup has been the wind speed sensor: its bearings need re-oiling every few months, or the readings start drifting low.'

Answer from recomposed context:
  Based on the provided context, the wind speed sensor needs re-oiling every few months.

Context shrank by 77% (685 -> 160 chars), with the same answer, ...
```

Both answers should say the same thing, the recomposed context isn't
answering a *different* question better, it's answering the *same*
question with roughly a quarter of the text, having thrown away the
sentences that were never going to help.

## Checkpoint

- **knowledge refinement**: decompose a chunk into strips, grade each,
  recompose the ones graded relevant into a new, shorter context, the
  paper's action for chunks graded "correct."
- Smaller context with an unchanged answer is the whole point: less
  irrelevant text for generation to potentially get distracted by or
  blend in, at effectively no accuracy cost on a clean example like
  this one.
- Lesson 12 puts this machinery to use: once refinement exists, grading
  can finally have three real outcomes (correct/ambiguous/incorrect)
  instead of two, because "ambiguous" now has somewhere useful to go,
  refine and keep, but flag for a possible rewrite too.

If anything here still feels unclear, ask before moving to Lesson 12.
