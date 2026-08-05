# Lesson 14: SqliteSaver, memory that survives a restart

## The limitation Lesson 13 left in place

`InMemorySaver` gives a graph real memory across `.invoke()` calls, but
only for as long as the Python process stays alive. Close the terminal,
and every thread's history is gone. This lesson swaps `InMemorySaver`
for `SqliteSaver`, which writes checkpoints to a real file on disk
instead of RAM.

## Swapping the checkpointer, nothing else changes

```python
with SqliteSaver.from_conn_string(str(DB_PATH)) as checkpointer:
    app = build_app(checkpointer)
```

Compare this to Lesson 13's `compile(checkpointer=InMemorySaver())`.
Everything about the graph itself, the node, the edges, the
`thread_id` pattern, stays identical. This is the exact payoff the
checkpointer interface is designed for: swapping where memory lives is
a one-argument change, because the rest of the graph was never written
against `InMemorySaver` specifically, only against "some object that
implements the checkpointer interface."

`SqliteSaver.from_conn_string(...)` opens a connection to a real
`.sqlite` file (SQLite is a small, file-based database, no server to
run) and hands it back as a context manager, so the connection closes
cleanly when the `with` block ends.

## Proof it's really on disk, not in memory

```python
DB_PATH = Path(__file__).parent / "checkpoints.sqlite"
```

This file lives in this lesson's own folder, and the script
deliberately never deletes it. Run the lesson, then run it again,
possibly minutes or days later, in a completely new `python` process,
with a completely new `SqliteSaver` connection: turn 2 in the second
run still knows the dog's name from the first run's turn 1. The only
place that fact could have survived is `checkpoints.sqlite` itself,
there is no Python object shared between the two runs at all.

```python
print(f"File size: {DB_PATH.stat().st_size} bytes")
```

You'll see this number grow between runs, real bytes on disk holding
real conversation history.

## Running it

```bash
uv run python lessons/langgraph/02_intermediate/14_persistent_checkpointer/lesson.py
```

Run it at least twice to see the persistence for yourself. The
`checkpoints.sqlite` file this creates is generated data, not source
code, safe to delete if you want to reset the demo.

## Checkpoint

- **`SqliteSaver`**: a checkpointer backed by a real file on disk,
  instead of `InMemorySaver`'s in-process RAM.
- **`from_conn_string(...)` is a context manager**: open it with `with`,
  build or use your graph inside the block.
- **swapping checkpointers is a one-line change**: because the rest of
  the graph is written against the same `checkpointer=` interface,
  regardless of which implementation backs it.
- **proof of persistence**: two totally separate runs, sharing nothing
  but a file path and a `thread_id`, still share memory correctly.

If anything here still feels unclear, ask before moving to Lesson 15,
where we pause a graph mid-run to wait for a human.
