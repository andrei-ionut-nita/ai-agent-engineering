# Lesson 16: get_state_history(), rewinding and forking a run

## What a checkpointer actually stores

Lessons 13-15 treated the checkpointer as a black box that "remembers
things." It's more specific than that: it saves a full snapshot of state
after every single node finishes, not just one final snapshot at the
end. This lesson looks directly at that history, and uses it to rewind
a graph to an earlier point and run forward again from there.

## Listing every snapshot

```python
history = list(app.get_state_history(config))
```

`get_state_history(config)` returns one `StateSnapshot` per checkpoint
for the given `thread_id`, newest first. For a 3-node linear graph like
this lesson's, that's five snapshots: one right after `START`, one after
each of `step1`, `step2`, and `step3` finishes.

```python
for snap in history:
    print(snap.next, snap.values)
```

Two fields matter most: `.values` is the state at that point, and
`.next` is a tuple naming whichever node was about to run next when that
snapshot was taken, empty once the graph reached `END`. So the snapshot
with `next=('step2',)` is the state exactly as it was right before
`step2` ran.

## Rewinding: pass an old checkpoint_id back in

```python
fork_config = {
    "configurable": {
        "thread_id": "history-demo",
        "checkpoint_id": before_step2.config["configurable"]["checkpoint_id"],
    }
}
replayed = app.invoke(None, fork_config)
```

Every `config` a snapshot carries already has a `checkpoint_id` baked
into it, `before_step2.config["configurable"]["checkpoint_id"]`. Passing
that specific ID back in, alongside the same `thread_id`, tells the
graph "resume from exactly this point in history," not from wherever the
thread currently sits (which, after the first `.invoke()`, is already at
the end). `None` as the input, same as resuming after Lesson 15's
`interrupt()`, means "just continue forward, no new data to add."

Verified directly in this repo: doing this re-runs `step2` and `step3`
starting from `before_step2.values` (`{'steps': ['step1'], 'total': 1}`),
landing back on the same final totals, because both step functions are
deterministic here. In general the replayed run can behave differently
if a node's logic depends on something that's changed since (the current
time, an external API's answer, or if you pass different `values` to
`update_state` before replaying), that's the actual point of time
travel: re-run a past decision under new conditions, rather than only
being able to look at history read-only.

## Why this matters beyond debugging

This is the same mechanism `interrupt()` in Lesson 15 depends on: a
paused thread is really just a graph sitting at a particular checkpoint,
waiting for a `Command(resume=...)` call to move it forward. Here we did
the same kind of forward-move manually, from a checkpoint we picked out
of the full history ourselves, useful for debugging ("what did the state
look like right before things went wrong?") or for building an "undo and
redo differently" feature into an application.

## Running it

```bash
uv run python lessons/langgraph/02_intermediate/16_time_travel_state_history/lesson.py
```

You'll see all five snapshots printed, then the state rewound to right
before `step2`, then the replayed result after running forward again.

## Checkpoint

- **`get_state_history(config)`**: lists every saved snapshot for a
  thread, newest first, one per node completion.
- **`StateSnapshot.next`**: which node was about to run when that
  snapshot was taken; empty once the graph reached `END`.
- **`checkpoint_id`**: identifies one specific snapshot; passing it in
  `config["configurable"]` alongside `thread_id` rewinds to that point.
- **`app.invoke(None, fork_config)`**: resumes forward from a rewound
  point, same "no new input" pattern as resuming after an `interrupt()`.

If anything here still feels unclear, ask before moving to Lesson 17,
where multiple nodes run at the same time instead of one after another.
