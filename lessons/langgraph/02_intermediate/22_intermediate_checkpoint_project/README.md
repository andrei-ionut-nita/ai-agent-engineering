# Lesson 22 (Checkpoint project): a persistent, human-in-the-loop content publishing workflow

## What this pulls together

This tier went from "a graph can remember things" (Lesson 13) all the
way to "a node can retry itself" (Lesson 21), nine separate ideas. This
project combines four of the most load-bearing ones into a single, small
but realistic workflow: draft a post, pause for human approval, and only
publish once approved, with real persistence and real failure recovery
along the way.

## The pieces, and which lesson each came from

```python
with SqliteSaver.from_conn_string(str(DB_PATH)) as checkpointer:
    app = builder.compile(checkpointer=checkpointer)
```

**Lesson 14's `SqliteSaver`.** Every workflow's state lives in a real
`.sqlite` file in this lesson's folder, not just in this process's RAM.
If this were a real app and the process crashed while a draft sat
waiting for approval, the pending approval would still be there,
recoverable, when the process came back.

```python
config = {"configurable": {"thread_id": thread_id}}
```

**Lesson 13's `thread_id`.** Each draft gets its own `thread_id`
(`"post-1"`, `"post-2"`), so one compiled graph can have many drafts
in flight, paused at different points, without any of them interfering
with each other.

```python
decision = interrupt({"question": "Approve this draft for publishing?", "draft": state["draft"]})
```

**Lesson 15's `interrupt()`.** `request_approval` pauses the graph and
surfaces the exact draft text for a human to review, before anything
irreversible happens. This script simulates the human's answer
immediately afterward with `Command(resume=...)`, but the checkpointer
above is exactly what would make a real, much later response safe.

```python
if decision:
    return Command(update={"approved": True}, goto="publish")
return Command(update={"approved": False}, goto="reject")
```

**Lesson 20's `Command`.** One node records the approval decision into
state AND decides whether to route to `publish` or `reject`, no separate
`add_conditional_edges` call needed for this branch.

```python
builder.add_node("publish", publish, retry_policy=RetryPolicy(max_attempts=3, initial_interval=0.1))
```

**Lesson 21's `RetryPolicy`.** `publish` simulates a real publishing API
that fails transiently on its very first call across the whole demo
(`publish_attempts == 1`). With the retry policy attached, that failure
is invisible from the outside, the workflow just succeeds, retried
automatically, exactly like the flaky node in Lesson 21.

## Reading the output

```
Topic: our new open-source CLI tool
  Draft: ...
  Paused, awaiting approval...
  -> Published!
```

Behind that one "Published!" line: the graph paused for a real approval
gate, its state was durable on disk the whole time it was paused, the
approval decision and the routing happened together in one node, and
the publish step silently recovered from a simulated outage. None of
that complexity is visible to whatever eventually reads the final
`published` field, which is the point, the pieces compose cleanly
because each one only does its own job.

## Running it

```bash
uv run python lessons/langgraph/02_intermediate/22_intermediate_checkpoint_project/lesson.py
```

The script clears `publishing.sqlite` at the start of each run purely so
its output is predictable to read here, a real deployment would never
do that, the whole point of `SqliteSaver` is that the file survives
between runs (Lesson 14).

## Checkpoint: this tier, end to end

- **memory** (Lessons 13-14): a checkpointer, keyed by `thread_id`, is
  what lets a graph remember state across separate `.invoke()` calls,
  either only for this process (`InMemorySaver`) or durably on disk
  (`SqliteSaver`).
- **pausing for humans** (Lesson 15): `interrupt()` halts a node and
  surfaces a payload; `Command(resume=...)` continues it later, from a
  potentially much later, separate call.
- **inspecting and rewinding history** (Lesson 16): `get_state_history()`
  exposes every checkpoint a run produced, and any of them can become a
  new starting point.
- **concurrency** (Lessons 17-18): nodes with no unmet dependencies in
  the same superstep run in parallel, whether the branches are fixed at
  build time (`add_edge` fan-out) or decided at runtime over a list
  (`Send`), as long as shared fields carry a reducer.
- **composition** (Lesson 19): a compiled graph can be embedded as a
  single node inside a bigger one.
- **routing that carries its own decision** (Lesson 20): `Command`
  updates state and picks the next node in one return value.
- **resilience** (Lesson 21): `RetryPolicy` recovers a node from
  transient failures automatically, without hand-written retry logic.

If anything across this tier still feels unclear, this is the moment to
go back to the specific lesson that introduced it. Otherwise, move on to
Lesson 23 in `03_advanced`, where these same primitives get used to
build an agent's ReAct loop entirely from scratch.
