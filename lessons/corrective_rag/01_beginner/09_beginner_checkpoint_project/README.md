# Lesson 9: Beginner Checkpoint - CLI Q&A That Self-Corrects

## What this is

No new concepts in this lesson. This is a checkpoint: a small, real
script built entirely out of ideas from Lessons 1 through 8, combined
into one thing, plus one small addition, a visible indicator of whether
correction actually fired. If you can read `lesson.py` and understand
why every piece is there, you've mastered the Beginner tier. If any
piece feels unfamiliar, that's a sign to revisit the lesson it came
from before continuing to Intermediate.

## What it does

Loads all five fixture notes, embeds and stores them (Lesson 2), then
answers three questions through `corrective_ask()`, printing whether
retrieval needed correcting for each one, so you can watch the pipeline
self-correct on the one question that needs it, and stay out of the way
on the two that don't.

## Where each piece came from

```python
def corrective_ask(query: str, store: list[dict], k: int = 3) -> tuple[str, bool]:
    retrieved = retrieve(query, store, k)
    naive_top1_source = retrieved[0]["source"] if retrieved else None
    ...
```

Lesson 8's `corrective_ask()`, with one addition: before grading
anything, it remembers what naive top-1 retrieval *alone* would have
used. That's not part of the corrective pipeline itself, it's purely
there so this lesson can report, honestly, whether correction changed
anything.

```python
    used_sources = {chunk["source"] for chunk in relevant}
    corrected = naive_top1_source is not None and naive_top1_source not in used_sources
```

The comparison: did the source that actually reached generation differ
from what naive top-1 would have used? If naive retrieval was already
right, `corrected` is `False`, correction didn't need to do anything,
and didn't pretend to.

## Running it

```bash
uv run python lessons/corrective_rag/01_beginner/09_beginner_checkpoint_project/lesson.py
```

## Expected output

```
Loaded and embedded 5 notes from .../fixtures/notes

Q: Project Aurora's Raspberry Pi writes sensor readings to a SQLite file on its SD card. Where does that Raspberry Pi physically live in the house?
  [retrieval was corrected]
A: Based on the provided context, Project Aurora's Raspberry Pi lives on a small shelf next to the bookshelf in the study...

Q: What's the cold ferment time for the pizza dough?
  [no correction needed]
A: Based on the provided context, the cold ferment time for the pizza dough is 48 hours.

Q: What is the capital of France?
  [retrieval was corrected]
A: I don't have any information relevant to that question.
```

The first question is this course's running example: naive top-1 would
have used `weather-station.md`, correction swaps in `bookshelf.md`
instead. The second question needed no correction, naive retrieval was
already right. The third question triggers correction (every candidate
graded not-relevant, a rewrite is attempted), but honestly can't invent
an answer this corpus was never going to contain.

## Try this yourself

Without looking anything up:

- Ask a question where naive top-1 retrieval is already correct (like
  the pizza dough one). Confirm `corrected` prints `False`, and that
  the pipeline didn't spend an extra grading call pretending it needed
  to fix something that wasn't broken. (It still spends one grading
  call to *confirm* the top result is relevant, that's expected.)
- Add a new `.md` file of your own to `fixtures/notes/`, does a question
  about it work correctly on the next run, with `[no correction
  needed]`?
- Lower `k` from 3 to 1 in `corrective_ask`'s default and re-run this
  course's running Aurora/bookshelf example. Does correction still fix
  it, and if not, which lesson explains why (hint: Lesson 4)?

If you can make these changes confidently, you're ready for the
Intermediate tier, starting at Lesson 10.
