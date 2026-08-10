# Lesson 19: Workflows

## What was hiding inside every QueryEngine

Every `index.as_query_engine()` call in this course, and every
`FunctionAgent` this course will use, is built on the same underlying
machinery: `Workflow`, from the separately-installed `llama-index-workflows`
package (`llama_index.core.workflow` re-exports it). A `Workflow` is a
small graph of `@step`-decorated methods that pass typed `Event` objects
to each other, an event-driven pipeline where each step declares, via
its own type hints, what triggers it and what it hands off next.

This lesson doesn't build anything new functionally, `as_query_engine()`
already does retrieve-then-synthesize in one line (Lesson 5). Instead it
hand-rolls that exact two-step pipeline as an explicit `Workflow`
subclass, to make visible the mechanism `as_query_engine()` normally
hides.

## Steps, Events, and how the graph gets wired

There's no explicit graph-building code, no `.add_edge()` calls the way
LangGraph's `StateGraph` requires. The wiring is implicit in each
`@step` method's type annotations:

```python
@step
async def retrieve(self, ev: StartEvent) -> RetrievedEvent: ...

@step
async def synthesize(self, ev: RetrievedEvent) -> SynthesizedEvent: ...

@step
async def finalize(self, ev: SynthesizedEvent) -> StopEvent: ...
```

`retrieve`'s parameter type (`StartEvent`) says it's an entry point.
`retrieve`'s return type (`RetrievedEvent`) is the exact type
`synthesize`'s parameter expects, so the Workflow knows `synthesize`
runs after `retrieve`. The same chain continues through `finalize`,
which returns `StopEvent`, the built-in exit point. Change a step's
declared input or output type and you've changed the graph, no separate
edge list to keep in sync.

| | LangGraph `StateGraph` | LlamaIndex `Workflow` |
|---|---|---|
| Wiring | Explicit `.add_edge()` calls | Implicit, inferred from step type hints |
| Shared data | One mutable state dict | Typed `Event` objects passed step to step |
| Entry/exit | `START` / `END` constants | `StartEvent` / `StopEvent` |

## The code, piece by piece

```python
class RetrievedEvent(Event):
    query: str
    context: str
    num_nodes: int
```

A custom `Event` subclass (a Pydantic model), the payload handed from
`retrieve` to `synthesize`. Small workflows typically have one custom
`Event` type per hand-off between steps.

```python
@step
async def retrieve(self, ev: StartEvent) -> RetrievedEvent:
    query = ev.query
```

`StartEvent` is the built-in entry point. Whatever keyword arguments get
passed to `.run()` show up as attributes on it, here `ev.query` because
the call below is `workflow.run(query=query)`.

```python
result = await workflow.run(query=query)
```

Runs the whole graph: `retrieve` fires first (its input type matches
`StartEvent`), its `RetrievedEvent` output triggers `synthesize`, whose
`SynthesizedEvent` output triggers `finalize`, which returns a
`StopEvent`. `result` is whatever was passed as `StopEvent(result=...)`,
here a dict.

## Why this matters beyond this one lesson

You will not usually hand-roll a two-step RAG pipeline this way, that's
what `as_query_engine()` and `FunctionAgent` are for. What this lesson
buys you is the ability to read LlamaIndex's own agent source code
(`llama_index/core/agent/workflow/function_agent.py`) and recognize the
exact same pattern: `@step` methods, custom `Event` subclasses,
`StartEvent`/`StopEvent`. It's also the tool to reach for when a real
pipeline needs a shape `as_query_engine()` doesn't offer, e.g. a
retrieve -> rerank -> fact-check -> synthesize chain with a branch,
without abandoning LlamaIndex's ecosystem for something like LangGraph.

## Running it

```bash
uv run python lessons/llamaindex/03_advanced/19_workflows/lesson.py
```

## Expected output

The LLM's exact wording will vary between runs, paraphrased below;
captured from a real run:

```
Hand-rolled 3-step Workflow: retrieve -> synthesize -> finalize

(This is the same shape of work index.as_query_engine() does for
you automatically, made visible as explicit steps and events.)

Q: What is Nimbus Robotics' policy on remote work equipment?
A: Based on the provided context, the policy on remote work equipment (home office equipment) is:

* Every employee receives a one-time 800 EUR stipend for a desk, chair, and monitor, which is reimbursed against receipts submitted within the first 60 days of employment.
* A company laptop is provided separately and is not part of this stipend.
  (synthesized from 2 retrieved nodes)
```

## Checkpoint

- **`Workflow`**: an event-driven pipeline of `@step`-decorated methods,
  the machinery underneath every QueryEngine and agent in this course.
- **`Event` subclasses**: typed payloads passed between steps; a step's
  parameter type says what triggers it, its return type says what runs
  next, no separate edge-list to maintain.
- **`StartEvent` / `StopEvent`**: built-in entry and exit points;
  `.run(**kwargs)` becomes attributes on `StartEvent`, `StopEvent(result=...)`
  becomes `.run()`'s return value.
- LangGraph's `StateGraph` wires steps explicitly with one shared mutable
  state; `Workflow` infers wiring from types and passes typed Events
  instead of a shared dict.

If anything here still feels unclear, ask before moving to Lesson 20.
