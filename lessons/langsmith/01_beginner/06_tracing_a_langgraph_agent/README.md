# Lesson 6: Tracing a LangGraph agent with no code changes

## What we're building

The identical calculator/word-counter ReAct agent from langgraph course,
lesson 23, run again unchanged, plus one config dict added to `.invoke()`
purely for organization. Every lesson before this one built tracing into
new code from scratch. This lesson proves you don't have to: anything
built with LangChain or LangGraph is traced automatically the moment
`LANGSMITH_TRACING=true` is set.

## What this reveals

`StateGraph`, `ToolNode`, `bind_tools`, every LangChain/LangGraph
component is already instrumented internally, the same way
`ChatGoogleGenerativeAI` was in Lesson 3. You never wrote a single
`@traceable` in this file. Compile the graph, invoke it, and the entire
run, the agent node deciding to call a tool, the tool executing, the
loop back to the agent, the final answer, shows up in LangSmith as a
full nested run tree, matching the graph's actual structure.

This is the practical reason LangSmith exists alongside LangChain and
LangGraph rather than as an unrelated add-on: for anything you build
with those two libraries, tracing is opt-in at the environment level,
not something you write into your application code.

The `config` dict passed to `.invoke()` here isn't required for tracing
to happen, it's already happening. It's there to make the resulting
trace more useful: `run_name` gives the top-level run a readable name
instead of a generic one, `tags` and `metadata` make it filterable
later (Lesson 18 covers filtering).

## The code, piece by piece

```python
builder = StateGraph(MessagesState)
...
app = builder.compile()
```

Unchanged from langgraph lesson 23, word for word.

```python
result = app.invoke(
    {"messages": [HumanMessage(question)]},
    config={
        "run_name": "calculator_word_counter_agent",
        "tags": ["langsmith-course", "langgraph-agent"],
        "metadata": {"lesson": 6},
    },
)
```

The only addition. `run_name` overrides the default run name LangSmith
would otherwise generate (usually the graph's internal name). `tags`
and `metadata` behave exactly as they did on `@traceable` functions in
Lesson 3, just passed through LangGraph's `config` argument instead.

## Running it

```bash
uv run python lessons/langsmith/01_beginner/06_tracing_a_langgraph_agent/lesson.py
```

In the UI, find the run named `calculator_word_counter_agent` and open
it. You should see the same node-by-node structure you'd see if you
called `app.get_graph()` locally, agent, tools, agent again, now as an
actual recorded run tree with real inputs and outputs at each step.

## Checkpoint

- **LangChain/LangGraph components trace themselves**: no
  `@traceable` needed for anything built from `StateGraph`, `ToolNode`,
  chat models, or other LangChain primitives, once tracing is on
  globally.
- **`config` on `.invoke()`**: the LangGraph/LangChain-native way to
  attach `run_name`, `tags`, and `metadata` to a run, equivalent to
  `@traceable`'s parameters or `langsmith_extra`.
- **Zero-instrumentation tracing**: existing LangChain/LangGraph
  applications get full observability just from an environment
  variable, no code changes.

If anything here still feels unclear, ask before moving to Lesson 7.
