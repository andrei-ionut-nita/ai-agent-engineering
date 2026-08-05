# Lesson 18: Send, fanning out dynamically over a list

## What Lesson 17 couldn't do

Lesson 17's parallel branches were fixed at graph-build time, always
exactly `summarize` and `extract_keywords`, no matter what input came
in. But plenty of real problems have a variable number of independent
jobs: process every item in a list, one worker per item, however many
items there happen to be. `Send` is LangGraph's answer to that, the
map half of a map-reduce pattern.

## dispatch(): returning Send objects instead of a node name

```python
def dispatch(state: TopicState):
    return [Send("worker", {"topic": topic}) for topic in state["topics"]]
```

This looks like a conditional edge function (Lesson 4), but instead of
returning a single node name to route to, it returns a **list** of
`Send` objects. Each `Send("worker", {...})` means "run the `worker`
node once, with exactly this state dict." Three topics in, three
separate `Send` objects out, three separate `worker` invocations, all
dispatched in the same superstep, running concurrently, same concurrency
model as Lesson 17's fixed fan-out.

## Each worker sees only its own slice

```python
class WorkerState(TypedDict):
    topic: str

def worker(state: WorkerState) -> dict:
    response = model.invoke(f"State one interesting fact about {state['topic']} in one sentence.")
    return {"facts": [f"{state['topic']}: {response.text.strip()}"]}
```

`worker()` never sees `state["topics"]`, the full list, or how many
other workers exist. Each `Send`'s dict (`{"topic": topic}`) is all that
particular invocation gets, deliberately isolated, the same way each
`Send("worker", {"topic": t})` call above is independent of the others.
This isolation is what makes the pattern safe to run concurrently at
all, no worker can step on another's input.

## Wiring it up

```python
builder.add_conditional_edges(START, dispatch, ["worker"])
```

Same `add_conditional_edges` call from Lesson 4, but the routing
function (`dispatch`) returns `Send` objects instead of a plain string.
The `["worker"]` list still declares which node names are reachable
here, useful for LangGraph's graph-visualization tooling (Lesson 11),
even though the actual number of dispatches only becomes known once
`dispatch` runs against real state.

## Reduce: gathering results back together

```python
facts: Annotated[list[str], operator.add]
```

Every worker's single-item return lands in this same shared field, same
reducer mechanism as Lesson 17's `findings`. `combine` runs once every
dispatched `worker` has finished (LangGraph tracks how many `Send`s went
out and waits for all of them), by which point `facts` already holds
every worker's contribution, however many there turned out to be.

## Running it

```bash
uv run python lessons/langgraph/02_intermediate/18_send_api_map_reduce/lesson.py
```

Change the `topics` list to have two entries, or five, and rerun, the
graph adapts automatically, no code changes needed, that's the whole
point of dispatching `Send` objects at runtime instead of hardcoding
branches.

## Checkpoint

- **`Send(node_name, state_dict)`**: dispatches one independent
  invocation of `node_name`, with its own isolated state.
- **map step**: a conditional-edge function returning a list of `Send`
  objects, one per item in a runtime-known list.
- **reduce step**: a shared, reducer-backed state field (`operator.add`)
  that collects every worker's contribution, plus a downstream node that
  waits for all of them.
- **workers are isolated**: each `Send`'s target node only ever sees
  that one `Send`'s state dict, not the full list or sibling workers.

If anything here still feels unclear, ask before moving to Lesson 19,
where a whole compiled graph gets reused as a single node.
