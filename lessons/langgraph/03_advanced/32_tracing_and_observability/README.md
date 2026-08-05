# Lesson 32: Tracing and observability, entirely local

## Seeing what actually happened

Beginner Lesson 8 introduced `stream_mode="updates"`, seeing which
node's output changed at each step. That's useful, but it doesn't show
timing, or the exact order events occurred in when a graph has both a
loop and a branch. `stream_mode="debug"` fills that in: it emits a
`"task"` event the moment a node starts, and a `"task_result"` event the
moment it finishes, each carrying a timestamp. This lesson reconstructs
a full execution trace from those two event types, without LangSmith,
without any external service, without anything beyond what every earlier
lesson already required.

## What a debug event looks like

```python
{'step': 2, 'timestamp': '...', 'type': 'task',
 'payload': {'id': '...', 'name': 'increment', 'input': {'count': 1}, ...}}

{'step': 2, 'timestamp': '...', 'type': 'task_result',
 'payload': {'id': '...', 'name': 'increment', 'result': {'count': 2}, ...}}
```

Every event carries a `step` number, a `type` (`"task"` for a node
starting, `"task_result"` for it finishing), and a `payload` with the
node's `name` and, for results, what it returned. The `id` field is
shared between a task and its matching result, that's how you know which
`task_result` belongs to which `task` when several nodes might be
involved.

## Matching starts to finishes

```python
started_at: dict[str, datetime] = {}

for event in app.stream({"count": 0}, stream_mode="debug"):
    payload = event["payload"]
    task_id = payload["id"]

    if event["type"] == "task":
        started_at[task_id] = datetime.fromisoformat(event["timestamp"])
        print(f"[step {event['step']}] -> entering {payload['name']} (input={payload['input']})")

    elif event["type"] == "task_result":
        elapsed = datetime.fromisoformat(event["timestamp"]) - started_at[task_id]
        print(f"[step {event['step']}] <- leaving  {payload['name']} (result=..., took {elapsed...}ms)")
```

Record the start time keyed by `id` when a task begins, compute the
elapsed time when its matching result arrives. This works correctly even
if a real graph runs multiple nodes concurrently (Intermediate Lesson
17's fan-out), each has its own `id`, so their timings never get mixed
up.

## A graph with both a loop and a branch

The lesson's graph increments a counter in a loop (same shape as
Beginner Lesson 5) until it reaches 3, then branches to `even_path` or
`odd_path` depending on whether the final count is even or odd. Running
it under `stream_mode="debug"` shows the loop's three passes through
`increment`, each with its own timing, followed by exactly one branch
taken, never both.

## Running it

```bash
uv run python lessons/langgraph/03_advanced/32_tracing_and_observability/lesson.py
```

You'll see steps 1 through 3 all entering and leaving `increment`, step 4
entering and leaving `classify`, and step 5 entering exactly one of
`even_path` or `odd_path`, each pair timed in milliseconds.

## Checkpoint

- **`stream_mode="debug"`**: emits `"task"` (node starting) and
  `"task_result"` (node finishing) events, each with a timestamp.
- **matching by `id`**: the shared `id` between a task and its result is
  how you compute per-node elapsed time, even under concurrency.
- **fully local**: no LangSmith, no extra API keys, this works offline
  aside from the Gemini calls the rest of the course already needs.
- **why this beats plain `print` statements**: you get exact ordering,
  step numbers, and timing without editing the node functions themselves
  at all.

If anything here still feels unclear, ask before moving to Lesson 33.
