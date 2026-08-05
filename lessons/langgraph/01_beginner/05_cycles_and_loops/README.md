# Lesson 5: Cycles, a conditional edge that routes backward

## Where we left off

Lesson 4's conditional edge always routed forward, to a node the graph
hadn't visited yet in that run. Nothing stops a routing function from
returning the name of a node earlier in the graph, including the very
node that's currently running. That's a **cycle**, and it's the single
biggest thing separating LangGraph from an LCEL chain.

## Why LCEL chains can't do this

An LCEL chain (`prompt | model | parser`, from the LangChain course) is
built with the `|` operator into a fixed pipe: data flows one direction,
through a fixed sequence of runnables, exactly once each. There is no
way to say "go back and run the second step again" inside that
structure, the pipe has no name for "the second step" that you could
route back to, it's just a sequence, not a graph with addressable
nodes.

LangGraph nodes are named and independently addressable, so a routing
function is free to send execution back to a node by name. That one
capability is what unlocks retry loops, "refine until good enough"
loops, and the ReAct think/act loop that Lesson 7 builds and Lesson 23
(advanced tier) generalizes. Without cycles, an agent could never decide
mid-task to try again.

## What we're building

A node that "grows" a piece of text by appending a word, that keeps
looping back to itself until the text reaches a target length, then
exits.

## The code, piece by piece

```python
class GraphState(TypedDict):
    text: str
    target_length: int
```

```python
def grow(state: GraphState) -> dict:
    return {"text": state["text"] + " more"}


def is_long_enough(state: GraphState) -> str:
    if len(state["text"]) >= state["target_length"]:
        return END
    return "grow"
```

`is_long_enough` is a routing function, same idea as Lesson 4, but
notice one of its possible return values is `END` itself, not just
another node's name. That's allowed, `END` is a valid conditional-edge
destination, meaning "stop the graph here."

```python
builder.add_conditional_edges("grow", is_long_enough)
```

Here's the cycle: this line wires `grow` to route either back to
`"grow"` (itself) or to `END`, depending on state. Every time `grow`
runs, it appends `" more"`, then `is_long_enough` checks the new length.
As long as the text is still too short, it loops back to `grow` again.
Once it's long enough, it routes to `END` and the graph stops.

## The safety net you'll meet properly in Lesson 10

If a routing function's condition could never become true (a bug, not a
loop by design), the graph would loop forever. LangGraph protects
against that with a `recursion_limit`, a maximum number of steps a
single `.invoke()` is allowed to take before it raises an error instead
of hanging. We're not touching that setting yet, this lesson's loop
genuinely terminates, but keep it in mind, Lesson 10 shows exactly what
happens when a loop doesn't stop in time.

## Running it

```bash
uv run python lessons/langgraph/01_beginner/05_cycles_and_loops/lesson.py
```

Watch the printed text grow across iterations, and note how many times
`grow` actually ran before the loop exited.

## Checkpoint

- **cycle**: a conditional edge routing back to a node the graph has
  already visited (including itself), something a straight-line LCEL
  chain cannot express.
- **`END` as a conditional-edge destination**: a routing function can
  return `END` directly to stop the graph, not just another node's name.
- **loop termination**: cycles rely on state eventually satisfying the
  routing function's exit condition, an always-false condition loops
  forever (Lesson 10 shows the safety net for that).

If anything here still feels unclear, ask before moving to Lesson 6.
