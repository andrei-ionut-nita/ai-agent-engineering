# Lesson 10: The config dict, and recursion_limit as a safety net

## Where we left off

Lesson 5 built a loop and mentioned, without demonstrating it, that
LangGraph protects against loops that never end. This lesson makes that
concrete: we deliberately trigger the failure, so you recognize it
immediately if you ever see it for real, and understand exactly why it
exists.

## The config dict

```python
app.invoke(initial_state, config={"configurable": {...}, "recursion_limit": 5})
```

Both `.invoke()` and `.stream()` accept an optional second argument,
`config`, a dictionary of run-level settings that aren't part of your
graph's state. State is the data your graph works on; config is
information about how to run it. You'll see `config["configurable"]`
carry a `thread_id` starting in Lesson 13 (intermediate tier) once
checkpointers give graphs memory, that's out of scope here. This lesson
only needs one key: `recursion_limit`, set directly on the config
dictionary (not nested inside `"configurable"`).

## What recursion_limit protects against

`recursion_limit` is the maximum number of **steps** (roughly, node
executions) a single `.invoke()` or `.stream()` call is allowed to take
before LangGraph gives up and raises a `GraphRecursionError`, instead of
running (or hanging) forever. It exists specifically because cycles
(Lesson 5) make infinite loops possible in a way a straight-line chain
never could: a routing function with a bug, or a condition that
genuinely can't be satisfied by the input given, would otherwise spin
forever, burning API calls and never returning. The default limit is
generous (25 at the time of writing), high enough that a well-behaved
loop won't hit it by accident, but low enough to eventually catch a
runaway one.

## Triggering it on purpose

```python
try:
    app.invoke({"text": "seed", "target_length": 30}, config={"recursion_limit": 3})
except GraphRecursionError as exc:
    print("Hit the safety net:", exc)
```

We reuse Lesson 5's grow-until-long-enough loop, which normally
finishes fine, but cap `recursion_limit` at 3, deliberately too low for
this loop to reach its target length. LangGraph raises
`GraphRecursionError` once the step count exceeds the limit, rather than
returning a wrong or partial answer silently. Catching it here (instead
of just crashing) shows what to check for if you ever see this error in
a graph you're actually debugging: either genuinely raise the limit for
a loop that legitimately needs more steps, or fix the routing condition
that isn't reaching its exit case.

## Running it

```bash
uv run python lessons/langgraph/01_beginner/10_invoke_config_and_recursion/lesson.py
```

You'll see the `GraphRecursionError` get raised and caught on purpose,
followed by the same loop succeeding normally once given a reasonable
limit.

## Checkpoint

- **`config`**: an optional dictionary passed to `.invoke()`/`.stream()`
  carrying run settings, separate from your graph's state.
- **`recursion_limit`**: the maximum number of steps a single run is
  allowed before LangGraph raises `GraphRecursionError`, a safety net
  against infinite cycles.
- **`GraphRecursionError`**: what you'll see if a loop (Lesson 5)
  legitimately needs more steps than the limit allows, or if a routing
  condition has a bug and never becomes true.

If anything here still feels unclear, ask before moving to Lesson 11.
