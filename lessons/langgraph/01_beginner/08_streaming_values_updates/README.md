# Lesson 8: Streaming a graph run, values vs. updates

## Where we left off

Every lesson so far has used `.invoke()`, which runs the whole graph and
hands you back the final state only once it's completely done. For a
graph with several steps, that means waiting for everything before
seeing anything. `.stream()` instead gives you a chunk of output after
every single node finishes, which matters a lot once graphs (or model
responses) take more than an instant to run.

## What we're building

Lesson 3's four-node text pipeline (clean, split, count, format),
streamed two different ways so you can see exactly what each
`stream_mode` gives you.

## The code, piece by piece

```python
for chunk in app.stream(initial_state, stream_mode="values"):
    print(chunk)
```

`stream_mode="values"` yields the **entire current state**, as it
stands, after each node finishes. Every chunk is a full snapshot, so if
your state has five fields and one node just changed one of them, you
still get all five fields back, just with that one field's new value.
This is the easiest mode to reason about because each chunk is
"complete," but it can repeat a lot of unchanged data on graphs with
many fields.

```python
for chunk in app.stream(initial_state, stream_mode="updates"):
    print(chunk)
```

`stream_mode="updates"` yields only the **diff**: a dictionary shaped
like `{"node_name": {the partial dict that node returned}}`. Instead of
the whole state, you get exactly what changed and which node changed
it. This is the mode to reach for when you care about "what just
happened" rather than "what does everything look like right now,"
useful for logging progress or driving a UI that shows per-step
activity.

## When to use which

Use `"values"` when you want to display or act on the state as a whole
at each step (say, showing the current draft of a document as it's
built up). Use `"updates"` when you want a clean, structured log of
which node did what, without extra fields cluttering each entry. Both
modes stream once per node execution, they differ only in what shape
of information you get for each step, not in when you get it.

## Running it

```bash
uv run python lessons/langgraph/01_beginner/08_streaming_values_updates/lesson.py
```

Compare the two printed sections: `"values"` will show growing/complete
state each time, `"updates"` will show small, node-labeled diffs.

## Checkpoint

- **`.stream()`**: runs a graph like `.invoke()`, but yields a chunk
  after every node finishes instead of only returning at the very end.
- **`stream_mode="values"`**: each chunk is the full current state
  snapshot.
- **`stream_mode="updates"`**: each chunk is just `{node_name: partial
  dict that node returned}`, the diff, not the whole state.

If anything here still feels unclear, ask before moving to Lesson 9.
