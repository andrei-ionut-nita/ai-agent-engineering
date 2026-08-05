# Lesson 15: interrupt(), pausing a graph mid-run for a human

## Why this matters

Every node so far has run to completion the moment it started, no
stopping point, no chance for a person to weigh in before something
happens. Real workflows sometimes need a human to see and approve an
exact action, an expense, a risky tool call, a public post, before it
actually goes through. `interrupt()` builds that stopping point directly
into a node.

## Calling interrupt() inside a node

```python
def request_approval(state: ExpenseState) -> dict:
    decision = interrupt(
        {"question": f"Approve expense of ${state['amount']} for '{state['reason']}'?"}
    )
    return {"approved": decision}
```

The first time `request_approval` runs for a given thread, `interrupt(value)`
pauses execution right there. `value` is whatever a human needs to see
to make a decision, here a small dict with the question. The graph halts
with its state already saved by the checkpointer (`interrupt()` requires
one, exactly like `interrupt_before` did for `create_agent` in the
langchain course's Lesson 30, pausing only makes sense if the in-progress
state is actually saved somewhere in the meantime).

## What .invoke() returns when it hits a pause

```python
result = app.invoke({...}, config)
pending = result["__interrupt__"]
print(pending[0].value["question"])
```

This was verified directly against this project's installed LangGraph
1.2.10: `.invoke()` does not raise and does not hang, it returns
normally, but the result dictionary carries an extra `"__interrupt__"`
key holding a list of `Interrupt` objects. `pending[0].value` is exactly
the dict we passed into `interrupt(...)` inside the node. `process_expense`
never ran, the graph stopped at `request_approval`.

## Resuming with Command(resume=...)

```python
final = app.invoke(Command(resume=True), config)
```

`Command(resume=True)` is a special input, not a plain state dict. It
tells the graph: "resume this exact thread, and wherever an `interrupt()`
call is waiting, hand it `True` as its return value." `request_approval`
re-executes from the top (the docs are explicit about this: the whole
node reruns, not just the line after `interrupt()`), but this time the
`interrupt()` call returns immediately with `True` instead of pausing
again, `decision` becomes `True`, and the node finishes normally.
Execution then continues on to `process_expense` as usual.

## Why the node reruns from the top

Because `interrupt()` works by re-executing the node and short-circuiting
past interrupt calls that already have an answer, code before an
`interrupt()` call inside the same node runs again on resume. Keep
anything with real side effects (sending an email, charging a card)
*after* the `interrupt()` call, or in a later node entirely, exactly
like `process_expense` here, which only runs once, after the resume.

## In a real app, this is two separate requests

```python
# In this demo script, both calls happen back to back:
result = app.invoke({...}, config)          # pauses
final = app.invoke(Command(resume=True), config)  # resumes, right away
```

In a real application these two calls would not be adjacent lines. The
first `.invoke()` would run when a user submits a request, and the
`"__interrupt__"` payload would be shown to a human reviewer through
some separate interface, an email, a dashboard, a Slack message. The
`Command(resume=...)` call would only happen later, from a completely
different process or HTTP request, once that person actually responded,
possibly minutes or days afterward. The checkpointer is what makes that
gap survivable, the graph's state sits safely on disk or in memory
between the two calls, waiting.

## Running it

```bash
uv run python lessons/langgraph/02_intermediate/15_human_in_the_loop_interrupt/lesson.py
```

You'll see two threads pause with their questions printed, then resume,
one approved, one rejected, purely by which value `Command(resume=...)`
carried.

## Checkpoint

- **`interrupt(value)`**: pauses the current node, surfaces `value` to
  whoever called `.invoke()`, requires a checkpointer.
- **`result["__interrupt__"]`**: how a paused `.invoke()` call reports
  what's pending, a list of `Interrupt` objects with a `.value`.
- **`Command(resume=...)`**: resumes a paused thread, the resumed value
  becomes `interrupt()`'s return value inside the node.
- **the node reruns from the top on resume**: keep side effects after
  the `interrupt()` call, or in a later node.
- **real usage is two separate calls, far apart in time**: this script's
  back-to-back calls are a stand-in for a human actually responding.

If anything here still feels unclear, ask before moving to Lesson 16,
where we look at the checkpoint history this pausing relies on.
