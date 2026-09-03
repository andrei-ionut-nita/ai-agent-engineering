# Lesson 14: Bounding Iterations

## Where we left off

Lesson 10's `while True` loop has an implicit assumption baked into it:
that the model will eventually stop asking for tool calls. Usually
true, not guaranteed. A confusing question, an ambiguous tool
description, or a tool that returns something unhelpful can all lead
the model to keep requesting calls indefinitely. This lesson adds the
guard that makes the loop provably terminate no matter what the model
does.

## The misconception this lesson corrects

It's tempting to think a step limit is only needed for hypothetical
"broken" agents, an edge case not worth the code. In production, it's
closer to a load-bearing requirement than an edge case: this loop makes
a real, billed API call and a real embedding call on every iteration,
so an unbounded version isn't just a theoretical infinite loop, it's an
uncapped cost and latency risk sitting in code that otherwise looks
identical to a safe one. `MAX_STEPS` isn't defensive pessimism, it's
the difference between "this function has a worst-case runtime" and
"this function might not."

## The code, piece by piece

```python
for step in range(1, MAX_STEPS + 1):
    ...
    if not calls:
        return response.text or "", step - 1, False
    ...
return ("I wasn't able to fully answer this within the allowed number of search steps. ...", MAX_STEPS, True)
```

The structural change from Lesson 10: `while True` becomes `for step in
range(1, MAX_STEPS + 1)`, so the loop body can run at most `MAX_STEPS`
times no matter what. If the loop exhausts its budget without the model
ever stopping on its own, the function falls through to an explicit,
honest fallback message, not a crash, not an empty string, not a
silent `None`.

## Why an honest fallback message, not just stopping

Returning nothing (or crashing) when the limit is hit would be worse
than the unbounded version it replaces: at least an infinite loop is
visibly broken; a function that silently returns an empty answer looks
like a normal, if unhelpful, response. Telling the caller explicitly
that the search was cut off, and that the answer might be incomplete,
is what makes this guard safe to actually deploy, the caller (a user, a
calling function) can act on that information instead of trusting an
answer that quietly might not be complete.

## Running it

```bash
uv run python lessons/agentic_rag/02_intermediate/14_bounding_iterations/lesson.py
```

## Expected output

```
Q: How often does the sourdough starter need feeding at room temperature?
  steps used: 1/4, hit limit: False
  A: The sourdough starter needs feeding every 12 hours at room temperature.
```

## Checkpoint

- **`MAX_STEPS`**: a hard cap on tool-call round trips, turning
  "probably terminates" into "provably terminates."
- Each loop iteration is a real, billed API call, an unbounded loop is
  an unbounded cost, not just a theoretical concern.
- Hitting the limit should return an honest, explicit "I couldn't fully
  answer this" message, never a silent empty result or a crash.
- This well-behaved question never comes close to the limit; Lesson 16
  studies a case designed to actually reach it.

If anything here still feels unclear, ask before moving to Lesson 15.
