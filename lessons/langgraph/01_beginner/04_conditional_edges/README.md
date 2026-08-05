# Lesson 4: Conditional edges, letting state decide what runs next

## Where we left off

Every graph so far has had exactly one path through it. Lesson 3's four
nodes always ran in the same order, no matter what the input text was.
Real workflows branch: "if the input looks like a question, do X, if it
looks like a statement, do Y." This lesson introduces the mechanism for
that: `add_conditional_edges`.

## What we're building

The pipeline from Lesson 3, but instead of always shouting the text,
it inspects the cleaned text and routes to one of two different nodes
depending on how long it is: short text gets expanded with a note, long
text gets truncated with a note.

## The code, piece by piece

```python
def route_by_length(state: GraphState) -> str:
    if len(state["text"]) <= 20:
        return "expand"
    return "truncate"
```

This is a **routing function**. It looks just like a node function,
state in, but instead of returning a partial state dict, it returns a
plain string: the name of whichever node should run next. It does not
modify state at all, its only job is to decide.

```python
builder.add_conditional_edges("clean_text", route_by_length)
```

`add_conditional_edges` replaces a plain `add_edge` when the next node
depends on state. Read as: "after `clean_text` finishes, call
`route_by_length` with the current state, and whatever node name comes
back is where execution goes next." LangGraph figures out which nodes
are reachable by looking at every string `route_by_length` could
possibly return, here that's `"expand"` and `"truncate"`, both of which
need to already be registered with `add_node`.

```python
builder.add_edge("expand", END)
builder.add_edge("truncate", END)
```

Both branches still need their own path to `END` (or onward to more
nodes), a conditional edge only decides which single node runs next, it
doesn't automatically wire up what happens after that. In a bigger
graph the branches might reconverge on a shared node instead of both
going straight to `END`, LangGraph doesn't care, you just draw whatever
edges make sense.

## Why this matters

This is the first genuinely new capability LangGraph gives you over
what you had in the LangChain course. LCEL's `RunnableBranch` (if you
saw it) can pick between a fixed set of runnables too, but it's still a
single decision made once, inline, as part of one chain. Here, routing
is a full first-class part of the graph: it can route to any node,
including nodes that themselves route again, and (Lesson 5) it can even
route back to a node the graph already visited, which is what a loop is.

## Running it

```bash
uv run python lessons/langgraph/01_beginner/04_conditional_edges/lesson.py
```

Run it once with a short input and once with a long one (the lesson
does both), and confirm each one takes the branch you'd expect.

## Checkpoint

- **routing function**: a function that takes state and returns a
  string, the name of the next node to run, it does not modify state.
- **`add_conditional_edges(source, routing_fn)`**: wires a node to more
  than one possible next node, chosen at runtime by the routing
  function's return value.
- **branches still need edges**: each possible destination of a
  conditional edge needs its own path onward (to `END` or elsewhere),
  a conditional edge only decides the very next hop.

If anything here still feels unclear, ask before moving to Lesson 5.
