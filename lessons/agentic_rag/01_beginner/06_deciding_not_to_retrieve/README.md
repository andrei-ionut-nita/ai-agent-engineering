# Lesson 6: Deciding Not to Retrieve

## Where we left off

Lesson 5 built a complete loop and ran it on a question that needed
retrieval. This lesson runs the *identical* loop, unchanged, on a
question that doesn't (general chemistry knowledge), specifically to
show the branch that Lesson 5's `if not calls:` line was written for
but never actually exercised, until now.

## The misconception this lesson corrects

A very natural assumption, especially after Lessons 3-5 spent so much
effort wiring up a tool call, is that **declaring a tool makes the
model use it**. It doesn't. `types.Tool(...)` makes a function call
*available*, one option among "answer directly" and "request a call."
The model still has to judge, per question, whether calling it would
actually help. This lesson's gold-symbol question is deliberately
something Gemini already knows cold, letting you watch that judgment
land on "no" instead of just asserting it can.

## The code, piece by piece

```python
def ask(query: str, store: list[dict]) -> tuple[str, bool]:
    ...
    calls = response.function_calls
    if not calls:
        return response.text or "", False
```

Nothing changed from Lesson 5's `ask()` except the return type, adding
a `bool` so `main()` can report whether `search_notes()` actually ran.
The branch itself, `if not calls: return response.text`, already
existed in Lesson 5, this lesson is the first time a question actually
takes it.

## Running it

```bash
uv run python lessons/agentic_rag/01_beginner/06_deciding_not_to_retrieve/lesson.py
```

## Expected output

```
Q: What is the chemical symbol for gold?
  Called search_notes(): False
  A: Au

Q: How often does Clarence the sourdough starter need feeding at room temperature?
  Called search_notes(): True
  A: Clarence needs feeding every 12 hours at room temperature.
```

If the gold question ever *does* trigger a tool call in your run
(small models are occasionally over-eager about calling declared
tools), that's not a bug in this lesson, it's the same imperfect
judgment this whole course is about: read `SEARCH_NOTES_DECLARATION`'s
description again and consider whether it's specific enough about
scope. That imprecision, not "the model is broken," is exactly the kind
of failure Lesson 16 studies deliberately later in this course.

## Checkpoint

- Declaring a tool makes a call *possible*, not mandatory, the model
  still judges whether a specific question needs it.
- The same `ask()` function, unmodified, correctly handles both "needs
  retrieval" and "doesn't need retrieval" questions, because the
  branching happens inside Gemini's own decision, not in this course's
  code.
- **Try this yourself**: write three more questions of your own, one
  clearly general knowledge, one clearly about the fixture notes, and
  one deliberately ambiguous (for example, "What's a good way to keep
  something from drying out?", which could plausibly be about the
  sourdough starter or just general advice). Run all three through
  `ask()`. Does the ambiguous one go the way you expected?

If anything here still feels unclear, ask before moving to Lesson 7.
