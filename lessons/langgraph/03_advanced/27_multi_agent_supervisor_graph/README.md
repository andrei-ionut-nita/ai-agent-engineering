# Lesson 27: Multi-agent supervisor graph

## Same idea as the langchain course, one level lower

`multi_agent_supervisor` (langchain course, lesson 31) wrapped entire
`create_agent` objects as tools, and handed them to a supervisor agent
that decided which one to call. This lesson builds the same structure
with raw LangGraph primitives: each specialist is a compiled `StateGraph`
(Intermediate Lesson 19's subgraph technique) rather than a
`create_agent` object, and the supervisor is a graph node with a
conditional edge, rather than an agent choosing among tools.

## Specialists are just Lesson 23, twice

```python
def build_specialist(tools: list, system_hint: str):
    bound_model = model.bind_tools(tools)
    def call_model(state: MessagesState) -> dict:
        response = bound_model.invoke([HumanMessage(system_hint), *state["messages"]])
        return {"messages": [response]}
    builder = StateGraph(MessagesState)
    builder.add_node("agent", call_model)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")
    return builder.compile()

math_specialist = build_specialist([calculator], "You are a math specialist...")
text_specialist = build_specialist([word_counter], "You are a text specialist...")
```

Nothing new here. This is Lesson 23's from-scratch ReAct loop, wrapped
in a function so it can be built twice with different tools and system
hints. Each specialist is a fully independent, fully compiled graph with
no idea a supervisor will ever call it.

## Plugging a compiled graph in as a node

```python
builder.add_node("math_specialist", math_specialist)
builder.add_node("text_specialist", text_specialist)
```

This is the key line. `add_node` doesn't care whether the second
argument is a plain function or an entire compiled `StateGraph`, as long
as the state schemas share compatible keys. Here, both the parent
`SupervisorState` and each specialist's `MessagesState` share a
`messages` key with the same `add_messages` reducer, so LangGraph runs
the whole specialist internally whenever that node is reached, and only
the `messages` key flows back out into the parent's state.

## The supervisor: a real node, not just a routing function

```python
def supervisor(state: SupervisorState) -> dict:
    decision = router_model.invoke(
        "Classify this request as 'math' ... or 'text' ...: "
        f"{state['messages'][-1].content!r}"
    )
    return {"route": decision.specialist}

def route_to_specialist(state: SupervisorState) -> Literal["math_specialist", "text_specialist"]:
    return "math_specialist" if state["route"] == "math" else "text_specialist"
```

The supervisor is a node like any other: it calls a structured-output
model (Lesson 24's pattern) to classify the request, and writes the
decision into state as `route`. A separate conditional edge function
then reads that field to decide where to send control. Splitting
"decide" (the node) from "route" (the conditional edge) keeps each piece
simple and easy to test independently.

## Running it

```bash
uv run python lessons/langgraph/03_advanced/27_multi_agent_supervisor_graph/lesson.py
```

You'll see each question routed to the correct specialist, and each
specialist's own internal tool-call loop (invisible from the supervisor)
producing the final answer.

## Checkpoint

- **subgraph as node**: a compiled `StateGraph` can be added directly
  with `add_node`, as long as its state schema shares compatible keys
  with the parent.
- **specialists don't know about the supervisor**: each one is fully
  independent, buildable and testable on its own.
- **supervisor node vs. routing function**: the node decides and writes
  state, a separate conditional edge function reads that state to route.
- **contrast with Lesson 26**: this is centralized, one supervisor
  decides for everyone, versus peers deciding for themselves.

If anything here still feels unclear, ask before moving to Lesson 28.
