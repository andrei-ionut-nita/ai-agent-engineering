# Lesson 12: Checkpoint, a text-processing pipeline graph

## What we're building

One graph that deliberately exercises everything from this tier: a
multi-field state with a reducer, a straight run of nodes, a
conditional branch, a loop, and a streamed run. The pipeline: clean
input text, classify it as either "short" or "long," branch to a
different transform node depending on which, and if the "long" branch's
result is still too long after transforming, loop back and shorten it
again until it fits, then format a final combined output.

```
START -> clean -> classify -+-> expand_transform ---+-> combine -> END
                             |                        |
                             +-> shrink_transform <-loop-+
                                    (loops back to itself until short enough)
```

## Wiring it up

```python
builder.add_edge(START, "clean")
builder.add_edge("clean", "classify")
builder.add_conditional_edges("classify", route_by_classification)
builder.add_conditional_edges("shrink_transform", is_short_enough)
builder.add_edge("expand_transform", "combine")
builder.add_edge("combine", END)
```

Nothing here is a new concept, every piece was covered in Lessons 1
through 11, this lesson's job is combining them in one graph instead of
introducing anything further:

- **State with a reducer** (Lesson 2): a `steps` field, `Annotated[list[str],
  operator.add]`, every node appends a short note of what it did, so the
  final state carries a full trail of what happened during the run.
- **A straight run of nodes** (Lesson 3): `clean` runs unconditionally
  first, `combine` runs unconditionally last.
- **A conditional branch** (Lesson 4): `route_by_classification` sends
  short text to `expand_transform` and long text to `shrink_transform`.
- **A loop** (Lesson 5): `shrink_transform` routes back to itself via
  `is_short_enough` until the text is under a target length, then
  continues on to `combine`.
- **Streaming** (Lesson 8): `main()` runs the graph with
  `app.stream(..., stream_mode="updates")` instead of a plain
  `.invoke()`, so you can watch each node's contribution as it happens,
  including every pass through the loop.

## Why no model call in this one

This checkpoint project deliberately stays in pure Python, no
`ChatGoogleGenerativeAI` call, so that what's being tested is graph
mechanics (state, reducers, branching, looping, streaming) on their
own, without a network call's latency or variability making the run
harder to follow. Lessons 6, 7, 9, and 11 already covered wiring a model
into a node and streaming its tokens, that skill combines with
everything here the moment you need it; nothing about adding a model
call here would exercise new graph mechanics.

## Running it

```bash
uv run python lessons/langgraph/01_beginner/12_beginner_checkpoint_project/lesson.py
```

Try both a short piece of input text and a long one (the lesson runs
both), and watch the streamed `"updates"` output to see the loop run
more than once on the long input before `combine` finally runs.

## Checkpoint: the whole beginner tier

- **state and reducers** (Lessons 1-2): a node returns a partial dict
  that's merged into state, plain fields use last-write-wins,
  `Annotated[type, reducer]` fields (like `operator.add` for lists)
  combine instead of overwrite.
- **wiring nodes** (Lesson 3): `add_node` registers a function under a
  name, `add_edge` connects node names, `START`/`END` mark the
  boundaries, `.compile()` then `.invoke()` runs it.
- **branching** (Lesson 4): `add_conditional_edges` with a routing
  function (state in, node name out) picks the next node at runtime.
- **cycles** (Lesson 5): a routing function can route back to a node
  already visited, something a straight-line LCEL chain cannot express,
  this is what makes retry and refine loops possible.
- **messages and models in nodes** (Lessons 6-7): `MessagesState` and
  `add_messages` for conversations, `ToolNode` and `tools_condition` for
  the think/act loop, both built from the same node/edge/cycle
  primitives as everything else.
- **streaming** (Lessons 8-9): `stream_mode="values"` (full snapshots),
  `"updates"` (per-node diffs), and `"messages"` (token-by-token from a
  model call inside a node) are three different granularities of
  watching a run happen instead of waiting for it to finish.
- **config and safety** (Lesson 10): the `config` dict carries run
  settings separate from state; `recursion_limit` stops a runaway cycle
  with `GraphRecursionError` instead of looping forever.
- **visualizing** (Lesson 11): `app.get_graph().draw_mermaid()` prints
  the compiled shape, useful for checking a graph matches what you
  intended once it's too big to picture from code alone.

You now have every primitive LangGraph gives you before memory enters
the picture. Lesson 13, starting the intermediate tier, adds
`InMemorySaver` and `thread_id` so a graph can remember previous runs,
the beginning of giving these graphs real memory across separate
`.invoke()` calls.

If anything here still feels unclear, ask before moving to Lesson 13
in `02_intermediate/`.
