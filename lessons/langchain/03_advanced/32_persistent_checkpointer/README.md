# Lesson 32: A persistent checkpointer, memory that survives a restart

## The limitation we've carried since Lesson 24

`InMemorySaver` (Lesson 24) gives an agent real memory across turns,
but that memory lives only inside the running Python process. Close the
program, and it's gone, the exact same limitation Lesson 17 flagged for
a plain Python list. This lesson swaps `InMemorySaver` for `SqliteSaver`,
which writes to a real file on disk instead.

## Swapping the checkpointer, nothing else changes

```python
with SqliteSaver.from_conn_string(str(DB_PATH)) as checkpointer:
    agent = create_agent(model=model, checkpointer=checkpointer)
```

Compare this to Lesson 24's `checkpointer=InMemorySaver()`. The rest of
`create_agent`, the rest of how you call `.invoke()`, the `thread_id`
pattern, none of it changes. This is exactly the payoff promised back
in Lesson 24: swapping to a persistent checkpointer is a one-line
change, because everything else was already built against the same
`checkpointer=` interface.

`SqliteSaver.from_conn_string(...)` opens a connection to a real
`.db` file (SQLite is a lightweight, file-based database, no separate
server needed) and returns it as a context manager, hence the `with`
block, the connection gets cleanly closed when the block ends.

## Simulating two separate program runs

```python
def session_one() -> None:
    with SqliteSaver.from_conn_string(str(DB_PATH)) as checkpointer:
        agent = create_agent(model=model, checkpointer=checkpointer)
        ...

def session_two() -> None:
    with SqliteSaver.from_conn_string(str(DB_PATH)) as checkpointer:
        agent = create_agent(model=model, checkpointer=checkpointer)
        ...
```

`session_two()` builds a **completely new** `agent` object, with a
**completely new** connection, sharing nothing with `session_one()`
except the `thread_id` and the path to the same `.db` file. This is
deliberately structured this way to prove a point: if `session_two()`
still remembers what was said in `session_one()`, it can't be because
some Python object was kept around in memory, there's no shared object
at all, only a shared file on disk.

## Proof it worked

Run the lesson: session one tells the agent "My favorite programming
language is Python." Session two, a genuinely separate agent and
connection, is asked "What is my favorite programming language?" and
answers correctly: "Your favorite programming language is Python!" The
only place that fact could have come from is the `memory.db` file
itself.

```python
print(f"File size: {DB_PATH.stat().st_size} bytes")
```

That `memory.db` file is real, sitting on disk in this lesson's folder
after you run it, you can inspect it, back it up, or delete it like any
other file (which is exactly why it's excluded from this project's git
history, generated data, not source code).

## Running it

```bash
uv run python lessons/langchain/03_advanced/32_persistent_checkpointer/lesson.py
```

## Checkpoint

- **`SqliteSaver`**: a checkpointer backed by a real file on disk,
  instead of `InMemorySaver`'s in-process memory.
- **swapping checkpointers is a one-line change**: because everything
  else in `create_agent` was already built against the same
  `checkpointer=` interface, since Lesson 24.
- **proof of real persistence**: two separate agent objects, two
  separate connections, sharing only a file path and a `thread_id`,
  still share memory correctly.

If anything here still feels unclear, ask before moving to Lesson 33.
