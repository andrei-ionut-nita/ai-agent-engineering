# Lesson 35: Advanced Capstone, a multi-agent research assistant graph

## What this is

No new concepts. This is the final checkpoint of the entire course: one
graph combining every major idea from the Advanced tier, and underneath,
everything from Beginner and Intermediate too. If you can read
`lesson.py` and explain why every piece is there, you've completed this
course's full arc, from a single `StateGraph` with one node in Lesson 1
to a durable, multi-agent, human-supervised graph here. It's analogous
in ambition to the langchain course's own capstone (langchain course,
lesson 35), built entirely with raw LangGraph primitives instead of
`create_agent`.

## What it does

A research assistant graph with:

- A supervisor routing each request to a specialist (Lesson 27)
- Two specialist subgraphs, each with its own tool-call loop (Lessons
  19, 23, 27)
- A local retrieval-flavored tool for the research specialist (Lesson 29)
- Persistent memory across turns via `SqliteSaver` (Lesson 14)
- A human-in-the-loop interrupt before a final, irreversible action
  (Lessons 15, 30)

## The supervisor and its two specialists

```python
research_specialist = build_specialist([search_notes], "You are a research specialist. ...")
math_specialist = build_specialist([calculator], "You are a math specialist. ...")
```

`build_specialist` is Lesson 23's from-scratch ReAct loop, reused
verbatim for both. Each specialist is a fully compiled `StateGraph`,
plugged into the parent graph as a single node, exactly Lesson 27's
subgraph-supervisor pattern.

```python
def route_from_supervisor(state: CapstoneState) -> str:
    return {
        "research": "research_specialist",
        "math": "math_specialist",
        "publish_report": "prepare_report",
    }[state["destination"]]
```

The supervisor's routing decision is structured output (Lesson 24), read
by a conditional edge. Requests that don't belong to either specialist,
here, anything asking to finalize or publish, get routed straight to the
report-preparation step instead.

## Memory that survives the whole session

```python
with SqliteSaver.from_conn_string(str(db_path)) as checkpointer:
    app = builder.compile(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "capstone-session"}}
    r1 = app.invoke(..., config)  # research question
    r2 = app.invoke(..., config)  # math question, SAME thread
    r3 = app.invoke(..., config)  # publish request, SAME thread
```

All three turns share one `thread_id`, so the checkpointer (Lesson 14)
carries the full conversation forward, the report prepared in the third
turn is built from everything discussed across all three, not just the
final message. This only works because `CapstoneState`'s `messages`
field uses `Annotated[list, add_messages]`, the same reducer shared by
both specialist subgraphs, so their internal exchanges merge cleanly
back into the parent's history.

## The approval gate before publishing

```python
def publish_report(state: CapstoneState) -> Command[Literal["__end__"]]:
    decision = interrupt(f"About to publish this report:\n{state['report_text']}\n\nApprove? (yes/no)")
    if str(decision).strip().lower() in {"yes", "y"}:
        message = AIMessage(f"Published.\n\n{state['report_text']}")
    else:
        message = AIMessage("Publish cancelled by reviewer.")
    return Command(goto=END, update={"messages": [message]})
```

Publishing is treated as irreversible, so it always pauses (Lesson 15's
mechanism), no threshold or condition decides whether to interrupt here,
every publish attempt gets reviewed. `Command` both applies the outcome
message and routes to `END` in one return value (Lesson 26's mechanism),
even though there's no peer hand-off involved, `Command` works equally
well for "route to a fixed destination based on a decision."

## Running it

```bash
uv run python lessons/langgraph/03_advanced/35_advanced_capstone_project/lesson.py
```

You'll see a research question answered by the research specialist, a
math question answered by the math specialist in the same thread, and
then a publish request that pauses for approval before printing the
final, assembled report.

## Checkpoint: a recap of the whole course

**Beginner (graph mechanics):** `StateGraph`, nodes, `add_edge`,
conditional edges, cycles, `MessagesState`, `ToolNode`, streaming, and
`config`, the raw pieces every graph in this course is built from.

**Intermediate (memory, persistence, control flow):** checkpointers
(`InMemorySaver`, `SqliteSaver`) for per-thread memory, `interrupt()` for
pausing on a human, time travel for rewinding state, fan-out/fan-in and
`Send` for parallelism, subgraphs for composing whole graphs as nodes,
and `Command` for updating state and routing in one step.

**Advanced (agents, multi-agent, production):** the ReAct loop built by
hand, structured output inside a node, `InMemoryStore` for cross-thread
memory, peer-to-peer handoffs versus a centralized supervisor, context
trimming, retrieval feeding generation, static versus dynamic
breakpoints, guardrail nodes, local observability, async concurrency,
and combining both kinds of memory for a real deployment, all of it
converging in this one graph.

Congratulations on completing the course.
