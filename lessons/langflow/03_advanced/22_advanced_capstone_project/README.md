# Lesson 22: Capstone. Langflow vs. raw LangGraph

## What we're comparing

Lesson 16's flow, unchanged, called exactly the way it was there, next
to `langgraph_equivalent.py`, a plain LangGraph agent with the same
two tools and the same model. Same behavior, same correct answer, two
very different artifacts sitting behind it. This is the trade-off this
whole course has been building toward, felt directly instead of read
about.

## Do this yourself

1. Open `lessons/langflow/02_intermediate/16_intermediate_checkpoint_project/flow.json`
   and `langgraph_equivalent.py` side by side.
2. In the Langflow flow, find where the model, the two tools, and the
   system prompt actually live, they're spread across several nodes'
   `template` fields, each restating its own full field schema.
3. In `langgraph_equivalent.py`, find the same three things, they're
   three short, ordinary Python definitions, `ChatGoogleGenerativeAI(...)`,
   two `@tool`-decorated functions, `bind_tools([...])`.
4. Make the same small change in both: add a third tool (a
   Celsius-to-Fahrenheit converter is a good one). In LangGraph, it's a
   new `@tool` function and one more entry in a list. In Langflow, it's
   a new Custom Component (Lesson 12's pattern) dragged onto the canvas
   and wired in. Notice which one is faster to *build*, and which one
   is faster to *review* a diff of afterward, they're not the same
   answer.

## The code, piece by piece

```python
langflow_answer = run_via_langflow(QUESTION)
```

Lesson 16's flow, called the exact same way, `upload_flow()` /
`run_flow()` from Lesson 11, nothing new here, this lesson's point
isn't a new Langflow feature, it's the comparison.

```python
model_with_tools = model.bind_tools([word_length, calculator])

def call_model(state: MessagesState) -> dict:
    return {"messages": [model_with_tools.invoke(state["messages"])]}

graph = StateGraph(MessagesState)
graph.add_node("agent", call_model)
graph.add_node("tools", ToolNode([word_length, calculator]))
graph.add_conditional_edges("agent", tools_condition)
graph.add_edge("tools", "agent")
```

The `langgraph` course's own agent pattern (`tools_condition`, a
prebuilt conditional edge that routes to the tools node when the model
asks for a tool call, back to the model otherwise), no Langflow
involved. If you've done that course, this should look completely
familiar, that's deliberate, it's the same underlying model, code
instead of canvas.

```python
langgraph_loc = len(LANGGRAPH_FILE.read_text().splitlines())
langflow_flow_bytes = LANGFLOW_FLOW_PATH.stat().st_size
```

Not a rigorous benchmark, a concrete number to anchor the point: one
side is something you'd read top to bottom in a code review, the other
is a byte count you'd trust a diff tool to summarize for you, or not,
Lesson 19's point again, from the other direction.

## Running it

```bash
uv run python lessons/langflow/03_advanced/22_advanced_capstone_project/lesson.py
```

## Expected output

Approximate for the two answers (both should be correct, and should
roughly agree with each other), exact for the file-size line's shape:

```
Question: How many letters are in the word 'checkpoint'?

Langflow's answer:   There are 10 letters in the word 'checkpoint'.
LangGraph's answer:  There are 10 letters in the word "checkpoint".

langgraph_equivalent.py: 63 lines of Python
Lesson 16's flow.json:   135,113 bytes of JSON, 0 lines you'd hand-review as code
```

## Where this leaves you

Neither side "wins." A flow built on a canvas gets you a working
prototype and a stakeholder demo faster than almost anything else, this
whole course is proof of that. But a flow that's going to live in a
codebase, get code-reviewed, and be maintained by a team benefits from
being code, not a big generated JSON blob, that's the graduation this
course has been pointing at since Lesson 2's README. Which one you
reach for depends on which side of that line you're actually on: still
proving the idea works, or making it something a team can own.

This is the last lesson in the course. If you've built and understood
every flow from `01_beginner/01_what_is_langflow` through here, you
know Langflow as more than a canvas, when to reach for it, when to
graduate past it, and how to do the graduating.
