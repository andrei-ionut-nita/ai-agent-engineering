# Lesson 10: Multi-Step Loops

## Where we left off

Every Beginner-tier lesson made at most one round trip: model call,
tool call if requested, one more model call, done. That's enough for a
single-fact question, but not for a compound one needing facts from two
different documents. This lesson replaces the `if`-based single round
trip with a `while` loop that keeps going as long as the model keeps
asking for tool calls.

## The misconception this lesson corrects

It's easy to read Lesson 5's loop and assume "the agent loop" is
inherently a one-shot thing: ask, maybe call a tool, answer. That's an
artifact of the *questions* used so far, not a limit of function
calling itself. Nothing about the API caps the number of round trips;
Lesson 5's `if not calls` was simply never exercised more than once.
This lesson's question is deliberately compound, needing the sourdough
note *and* the aquarium note, so a single `search_notes()` call
genuinely cannot answer it.

## The code, piece by piece

```python
def search_notes(query: str, store: list[dict], k: int = 1) -> str:
```

`k` drops from 2 to 1 this lesson, on purpose. With `k=2`, a single
call might accidentally surface both relevant notes anyway (there are
only five in the whole store), hiding the multi-step behavior this
lesson is trying to demonstrate. `k=1` makes each call genuinely
single-document, so a two-part question forces two calls.

```python
while True:
    response = client.models.generate_content(model=CHAT_MODEL, contents=contents, config=CONFIG)
    calls = response.function_calls
    if not calls:
        return response.text or "", steps
    ...
```

The structural change from every earlier lesson: what was an `if` is
now a `while True`, with the same body, appending the model's call turn
and the tool's result turn to `contents` each iteration, looping back
to call `generate_content()` again with the growing transcript. The
loop only exits when a turn comes back with no function call, meaning
the model judged it now has enough information to answer.

## Why the description had to change too

`SEARCH_NOTES_DECLARATION`'s description now explicitly says results
come from "ONE source document at a time" and invites another call for
a different query. This isn't decoration, without it the model has no
particular reason to call the tool twice instead of assuming one call's
result is all there is; Lesson 11 studies this kind of instruction
(steering the model toward decomposing a compound question) directly.

## Running it

```bash
uv run python lessons/agentic_rag/02_intermediate/10_multi_step_loops/lesson.py
```

## Expected output

```
Q: What's the feeding schedule for the sourdough starter, and separately, how often should the aquarium's filter sponge be rinsed?
search_notes() was called 2 time(s)
A: <a combined answer citing the 12-hour feeding schedule and the every-other-water-change filter rinse>
```

`steps` should be 2. If it comes back as 1, the model likely combined
both facts from a single lucky retrieval, rare with `k=1` and five
topically distinct notes, but not impossible; re-running usually
reproduces the two-step behavior.

## Checkpoint

- Nothing in the function-calling API limits round trips to one, the
  Beginner tier's `if not calls` and this lesson's `while True` are the
  same loop, generalized.
- `k=1` deliberately forces single-document retrieval per call, so a
  compound question needs more than one call to answer completely.
- The tool's own description is part of what makes multi-step behavior
  reliable, it needs to tell the model that one call doesn't
  necessarily cover everything.
- Without a step limit, this loop could in principle run forever if the
  model kept requesting calls. Lesson 14 adds the guard; Lesson 16
  studies what happens without one.

If anything here still feels unclear, ask before moving to Lesson 11.
