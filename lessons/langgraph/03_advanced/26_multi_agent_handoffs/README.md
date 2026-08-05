# Lesson 26: Multi-agent handoffs

## A different shape than a router

So far, every routing decision in this course has come from one place: a
conditional edge, examining state, sending control to exactly one named
node. This lesson uses a different shape entirely: a node decides, from
inside itself, to hand control directly to a specific peer. There's no
central router involved in that decision at all. Intermediate Lesson 20
introduced `Command` for updating state and routing in one return value;
this lesson uses that same mechanism for a new purpose, peer-to-peer
handoffs.

## Two peers, each able to redirect to the other

```python
def billing(state: MessagesState) -> Command[Literal["tech_support", "__end__"]]:
    ...
    if decision.handoff_to == "tech_support":
        return Command(
            goto="tech_support",
            update={"messages": [AIMessage(f"[billing] {decision.reply}")]},
        )
    return Command(goto=END, update={"messages": [AIMessage(f"[billing] {decision.reply}")]})
```

`billing` is a normal node function, but instead of returning a plain
dict, it returns a `Command`. `update={...}` behaves exactly like a
returned dict always has, it merges into state. `goto=...` is the new
part: it names the *next* node directly, bypassing whatever edges were
declared with `add_edge` or `add_conditional_edges`. `tech_support` is
written as a mirror image: it can hand off back to `billing` under its
own conditions.

## The graph has almost no edges

```python
builder.add_edge(START, "billing")
```

That's the only `add_edge` call in this lesson. Every other transition,
`billing -> tech_support`, `tech_support -> billing`, either one to
`END`, is decided at runtime by the `Command` each node returns. This is
the defining trait of the handoff pattern: peers route to each other
directly, the graph's static structure barely constrains where control
can go next.

## Deciding whether to hand off

```python
class Routing(BaseModel):
    handoff_to: Literal["tech_support", "billing", "none"] = Field(...)
    reply: str = Field(...)

router_model = model.with_structured_output(Routing)
```

Each node asks a small structured-output call (Lesson 24's pattern):
"does this request actually belong to my peer?" If yes, hand off with a
short note explaining why. If no, answer directly and end the turn. The
structured `reply` field doubles as both the handoff explanation and, if
no handoff happens, the actual answer to the user.

## Running it

```bash
uv run python lessons/langgraph/03_advanced/26_multi_agent_handoffs/lesson.py
```

Ask a technical question and watch execution start at `billing`, decide
it doesn't belong there, and jump straight to `tech_support`, which then
answers directly, no supervisor ever consulted. Lesson 27 shows the
opposite structure: a single supervisor deciding everything up front.

## Checkpoint

- **`Command(goto=..., update={...})`**: updates state and routes to a
  named node in one return value, overriding normal edges.
- **peer-to-peer handoff**: a node decides, from inside itself, to
  redirect control to a specific other node, no central router involved.
- **minimal edges**: when nodes route via `Command`, the graph's
  declared edges shrink down to little more than the entry point.
- **contrast with Lesson 27**: handoffs are decentralized (any peer can
  redirect); a supervisor graph is centralized (one node decides for
  everyone).

If anything here still feels unclear, ask before moving to Lesson 27.
