# Lesson 17: Graph-based control flow with `pydantic_graph`

## The `langgraph` equivalent, for explicit multi-step flows

Lesson 12's delegation pattern works well when one agent decides
whether to call another. Sometimes you want the *sequence itself*
fixed and explicit: always run step A, then step B, then step C,
regardless of what any single LLM call decides. That's what
`langgraph` gives LangChain agents; `pydantic_graph` gives Pydantic AI
the same thing, typed steps and edges instead of a graph of nodes.

## Building a graph

`GraphBuilder` is where a graph is assembled: declare the input/output
types, add steps, wire edges between them, then `build()`.

```python
from pydantic_graph import GraphBuilder

builder = GraphBuilder(input_type=str, output_type=str)

@builder.step
async def write_joke(ctx) -> str:
    result = await agent.run(ctx.inputs)
    return result.output

@builder.step
async def add_rimshot(ctx) -> str:
    return ctx.inputs + "\n*rimshot*"

builder.add_edge(builder.start_node, write_joke)
builder.add_edge(write_joke, add_rimshot)
builder.add_edge(add_rimshot, builder.end_node)

graph = builder.build()
result = graph.run_sync(inputs="cats")
```

Every `@builder.step` function is `async` and receives a `StepContext`
whose `.inputs` is whatever the previous step (or the initial call)
produced. `builder.start_node` and `builder.end_node` are fixed
markers you wire your own steps to; `add_edge(a, b)` means "after `a`
finishes, run `b`."

## Calling an agent from inside a step

Because a step is already `async`, call the agent with `await
agent.run(...)`, not `run_sync`, calling the sync version from inside
a running event loop raises `RuntimeError: This event loop is already
running`. This mirrors calling an LLM from inside a LangGraph node: the
node function is async, so the model call inside it is awaited too.

## When to reach for this over Lesson 12's delegation

Delegation-as-a-tool suits "the model decides whether and when to call
a specialist." A graph suits "this sequence of steps always happens in
this order," validation, then transformation, then a side effect, with
no LLM in the loop deciding the *order*, even if individual steps call
an LLM internally. `langgraph` proper adds cycles, shared state, and
much richer branching on top of this same idea, if a graph like this
one grows past a straight line.

## Running it

```bash
uv run python lessons/pydantic_ai/02_intermediate/17_graph_based_agents_with_pydantic_graph/lesson.py
```

## Checkpoint

- `GraphBuilder(input_type=..., output_type=...)`, `@builder.step`,
  and `add_edge(a, b)` are the three pieces of building a graph.
- A step's `ctx.inputs` is the previous step's output; `start_node` and
  `end_node` are the fixed entry/exit markers.
- Steps are async; call an agent inside one with `await agent.run(...)`,
  not `run_sync`.

If anything here still feels unclear, ask before moving to Lesson 18.
