# Lesson 6: Tools, the basics

## `@agent.tool_plain`: a function the model can call

A tool is a Python function the model can decide to invoke mid-run,
exactly the idea behind `@tool` in the `langchain` course. The simplest
form doesn't need any runtime context:

```python
@agent.tool_plain
def add(a: int, b: int) -> int:
    """Add two integers together."""
    return a + b
```

Pydantic AI reads the function's type hints to build the tool's JSON
Schema (so `a` and `b` must be integers), and reads the docstring to
build its description (so the model knows what the tool does and,
with a Google/NumPy-style docstring, what each parameter means). This
is exactly how LangChain's `@tool` decorator worked, same source of
truth: types and docstrings, no separate schema to maintain by hand.

## What happens when the model calls a tool

You don't write a tool-calling loop yourself. Call `run_sync` once;
internally, Pydantic AI sends the model the prompt plus the tool
schemas, and if the model decides to call one, Pydantic AI runs your
Python function, feeds the result back to the model, and repeats until
the model produces a final answer. All of that happens inside a single
`run_sync` call.

```python
result = agent.run_sync("What is 12 plus 30? Use the tool.")
print(result.output)  # "42" already incorporated into a full answer
```

Compare this to `langchain/14_tool_calling` and `16_agent_executor`,
where you built that loop by hand (or reached for `AgentExecutor`) to
get the same behavior. Here it's just what `run_sync` does whenever
the agent has tools registered.

## `tool_plain` vs `tool`

`tool_plain` is for tools that need nothing beyond their own
arguments. Lesson 7 covers `@agent.tool`, the version that also
receives a `RunContext` so the tool can read `ctx.deps`.

## Running it

```bash
uv run python lessons/pydantic_ai/01_beginner/06_tools_basics/lesson.py
```

## Checkpoint

- `@agent.tool_plain` registers a function the model can call, schema
  and description come from type hints and the docstring.
- The full ask/call/respond loop happens inside one `run_sync` call,
  no `AgentExecutor` or manual loop needed.
- This is the direct Pydantic AI equivalent of `@tool` +
  `bind_tools` + the tool-calling loop from the langchain course.

If anything here still feels unclear, ask before moving to Lesson 7.
