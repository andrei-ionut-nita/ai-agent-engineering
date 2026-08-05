# Lesson 20: Command, updating state and routing in one step

## Two mechanisms, one job, since Lesson 4

Since Lesson 4, routing has always been two separate pieces working
together: a node returns a plain dict to update state, and then a
completely separate `add_conditional_edges` call, wired onto that node,
inspects the resulting state and decides where execution goes next. That
split works fine, but it means the logic for "what did we decide" and
"where does that decision send us" live in two different places, a node
function and a routing function, that have to stay in sync by hand.
`Command` merges them into one.

## A node that returns Command instead of a dict

```python
def classify_and_route(state: ReviewState) -> Command[Literal["handle_positive", "handle_negative"]]:
    verdict = model.invoke(...).text.strip().lower()
    if "positive" in verdict:
        return Command(update={"sentiment": "positive"}, goto="handle_positive")
    return Command(update={"sentiment": "negative"}, goto="handle_negative")
```

`Command(update={...}, goto="node_name")` does both jobs at once:
`update` is applied to state exactly like a returned dict always has
been, and `goto` names the next node directly, no conditional-edge
function gets consulted at all for this node's outgoing path. The
`Command[Literal["handle_positive", "handle_negative"]]` return
annotation is optional but worth keeping, it documents (and lets tooling
like Lesson 11's graph visualization understand) which destinations this
node can actually route to.

## Wiring: notice what's missing

```python
builder.add_edge(START, "classify_and_route")
builder.add_edge("handle_positive", END)
builder.add_edge("handle_negative", END)
```

Compare this to Lesson 4, which would need an `add_conditional_edges`
call here. There isn't one. `classify_and_route`'s `Command` return
value already fully determines where execution goes after it runs,
`add_edge` is only still needed for the two nodes whose next step never
varies (`handle_positive` and `handle_negative` always lead to `END`).

## When to reach for Command over conditional edges

Both approaches produce identical graphs. `add_conditional_edges`
(Lesson 4) keeps "what happens" and "where next" visually separate,
useful when many different nodes might all route to the same place, or
when you want the full set of possible transitions declared in one spot
near the graph-building code. `Command` keeps the decision and the
routing together at the point they're actually computed, useful when a
single node is naturally the one place that knows the answer to both
questions at once, exactly like `classify_and_route` here, which already
had to know the sentiment before it could possibly know where to send
it.

## Running it

```bash
uv run python lessons/langgraph/02_intermediate/20_command_objects/lesson.py
```

One positive review and one negative review, each correctly routed to
its own handler node, with `sentiment` set by the same `Command` object
that did the routing.

## Checkpoint

- **`Command(update={...}, goto="node")`**: returned from a node, applies
  a state update and routes to a specific next node in one step.
- **replaces `add_conditional_edges` for that node**: a node returning
  `Command` needs no separate conditional-edge call for its own routing.
- **still fully compatible with normal `add_edge`**: nodes with fixed,
  unconditional next steps still just use `add_edge`, same as always.
- **choose based on where the decision naturally lives**: keep routing
  logic separate (Lesson 4) when several nodes share it, or collapse it
  into the node (`Command`) when one node already computes the answer.

If anything here still feels unclear, ask before moving to Lesson 21,
where a node recovers automatically from transient failures.
