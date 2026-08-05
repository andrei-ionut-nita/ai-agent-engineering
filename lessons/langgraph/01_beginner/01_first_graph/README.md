# Lesson 1: A graph that does nothing but wire two boxes together

## What we're building

The absolute smallest possible LangGraph program: one piece of state,
one node, two edges. No AI model, no tools, nothing that talks to the
network. The point of this lesson is to see the mechanical shape of a
graph before anything else gets layered on top of it.

## Why a graph at all

You finished the LangChain course knowing `.invoke()`, LCEL chains, and
`create_agent`. Those all work great for "step 1 happens, then step 2,
then step 3" or even "the model decides which tools to call, in a loop,
until it's done." But LCEL chains are still fundamentally a straight
line (or a tree that piping combinators like `RunnableParallel` can
branch), and `create_agent`'s loop is baked in and fixed. When you need
custom control flow, "go back and retry this specific step," "branch
three different ways depending on what the data looks like," "run five
things in parallel then merge them," you need something that lets you
draw that shape explicitly.

LangGraph is that something. Instead of chaining objects together with
`|`, you build an actual graph: a set of named **nodes** (plain
functions) connected by **edges** (which node runs after which). You
get to decide the shape completely, including shapes that loop back on
themselves, which is something a straight-line chain cannot do at all.
That's the whole subject of this course. Lesson 5 shows a loop
concretely, but first we need the pieces a loop is built from.

## The code, piece by piece

```python
class GraphState(TypedDict):
    text: str
```

Every LangGraph graph needs a **state** definition: a description of
what data flows through the graph as it runs. Here it's a `TypedDict`
(the same typing tool you'd use for a plain dictionary with known keys)
with a single field, `text`, that will hold a string. This is not an
instance, it's a schema, LangGraph uses it to know what shape of
dictionary to expect at every step.

```python
def shout(state: GraphState) -> dict:
    return {"text": state["text"].upper()}
```

This is a **node**: an ordinary Python function that takes the current
state and returns a dictionary of the fields it wants to change. `state`
comes in as a dictionary matching `GraphState`'s shape. `shout` reads
`state["text"]`, uppercases it, and returns `{"text": ...}`, a partial
update, not the whole state object. LangGraph merges whatever a node
returns back into the overall state (Lesson 2 covers exactly how that
merge works when there's more than one field).

```python
builder = StateGraph(GraphState)
builder.add_node("shout", shout)
```

`StateGraph(GraphState)` creates a graph builder that knows to expect
state matching the `GraphState` schema. `add_node` registers the
`shout` function under the name `"shout"`, the string name is what
you'll use everywhere else (edges, routing) to refer to this node,
it doesn't have to match the function's Python name, though keeping
them matching makes graphs much easier to read.

```python
builder.add_edge(START, "shout")
builder.add_edge("shout", END)
```

`add_edge` draws a line from one node to the next. `START` and `END`
are special constants LangGraph provides, they're not real nodes you
wrote, they mark where a graph run begins and where it's allowed to
finish. This graph's shape is as simple as it gets: start, run
`shout`, end.

```python
app = builder.compile()
```

`.compile()` checks the graph you built (are all the nodes reachable,
does every path eventually reach `END`, and so on) and turns it into a
runnable object. You build the graph's shape once with `add_node` and
`add_edge`, then compile it once, then you can `.invoke()` the compiled
`app` as many times as you want.

```python
result = app.invoke({"text": "hello graph"})
```

`.invoke()` takes an initial state dictionary, runs it through the
graph following the edges you drew, and returns the final state as a
dictionary. Here that means: start with `{"text": "hello graph"}`, run
it through `shout`, get back `{"text": "HELLO GRAPH"}`.

## Running it

```bash
uv run python lessons/langgraph/01_beginner/01_first_graph/lesson.py
```

## Expected output

No AI model is involved here, so this output is exact, not approximate:

```
Input:  hello graph
Output: HELLO GRAPH
```

If you see an error instead, check the
[Troubleshooting section](../../../../README.md#troubleshooting) in
this project's root README.

## Checkpoint

- **state**: the shape of data (a `TypedDict`) that flows through a
  graph, defined once and passed to `StateGraph`.
- **node**: a plain function, `state in, partial dict out`, registered
  with `add_node` under a string name.
- **edge**: a connection from one node's name to another, drawn with
  `add_edge`, `START` and `END` mark where a run begins and can finish.
- **`.compile()`**: turns the wired-up graph into something you can
  actually run, do this once after all nodes and edges are added.
- **`.invoke()`**: runs one input through the compiled graph and
  returns the final state.

If anything here still feels unclear, ask before moving to Lesson 2.
