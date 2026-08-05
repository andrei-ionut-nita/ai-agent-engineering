# Lesson 17: fan-out and fan-in, running nodes at the same time

## Supersteps: LangGraph's unit of execution

Every graph run so far has felt like a straight line, one node, then the
next, in the order the edges implied. Under the hood, LangGraph actually
runs in rounds called **supersteps**: in each round, every node whose
dependencies are already satisfied runs, and if more than one node
qualifies in the same round, they run concurrently, not one after
another. Every graph up to Lesson 16 happened to have exactly one node
ready per round. This lesson is the first one where that's not true.

## Fan-out: two edges from one node

```python
builder.add_edge(START, "summarize")
builder.add_edge(START, "extract_keywords")
```

Both `summarize` and `extract_keywords` depend only on `START`, nothing
else. So in the very first superstep, both of them are ready at the
same time, and LangGraph runs them concurrently instead of picking one
to go first. Each one reads the same `text` field and does independent
work, one summarizes, the other pulls out keywords, neither knows or
cares that the other is running.

## The reducer that makes fan-in safe

```python
findings: Annotated[list[str], operator.add]
```

Both branches write to `findings` in the same superstep. Without a
reducer here, LangGraph would have no way to know whether that's a
genuine conflict (two nodes disagreeing about state) or two contributions
that should both be kept, and it raises an error rather than silently
picking one. `operator.add` (same reducer from Lesson 2, now doing real
work under concurrency) tells it explicitly: concatenate the lists, keep
both nodes' single-item contributions.

## Fan-in: waiting for every branch to finish

```python
builder.add_edge("summarize", "combine")
builder.add_edge("extract_keywords", "combine")
```

`combine` has two incoming edges. LangGraph only runs a node once every
edge pointing into it is satisfied, so `combine` waits for both
`summarize` and `extract_keywords` to finish, however long each one
individually takes, before it ever runs. By the time `combine` sees
`state["findings"]`, both contributions are already merged in, it
doesn't need to know how many branches fed into it.

## Running it

```bash
uv run python lessons/langgraph/02_intermediate/17_parallel_fan_out_fan_in/lesson.py
```

You'll see two findings printed, a summary and a set of keywords, both
produced by nodes that ran in the same superstep, then combined into one
block of text. The order they print in can vary between runs, since
they genuinely ran concurrently.

## Checkpoint

- **superstep**: LangGraph's unit of execution; every node with
  satisfied dependencies in a given round runs, concurrently if there's
  more than one.
- **fan-out**: multiple `add_edge` calls from the same node send
  execution down multiple branches at once.
- **fan-in**: a node with multiple incoming edges waits for all of them
  before running.
- **reducer required for shared writes**: any state field more than one
  parallel branch writes to needs an `Annotated[..., reducer]`, or
  LangGraph raises an error instead of guessing how to merge.

If anything here still feels unclear, ask before moving to Lesson 18,
where the number of parallel branches is decided at runtime, not fixed
when you build the graph.
