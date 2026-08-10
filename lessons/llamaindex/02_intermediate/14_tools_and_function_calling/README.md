# Lesson 14: Tools and function calling

## The step before a full agent

Lessons 1-13 built and queried indexes, but everything the LLM did came
from retrieved documents or from what it already knew, it never reached
out and *did* something. This lesson introduces the piece that makes that
possible: a `FunctionTool`, a plain Python function wrapped so an LLM can
decide to call it and see the result.

This is deliberately the smallest possible version of tool calling, one
tool, one decision, no loop. Lesson 15 builds the real thing on top of it,
a `FunctionAgent` that can call tools repeatedly, reasoning across
multiple steps toward a final answer. Understanding this lesson's single
decision first makes that loop much easier to read.

| | LangChain | LlamaIndex |
|---|---|---|
| Wrap a function as a tool | `@tool` decorator | `FunctionTool.from_defaults(fn=...)` |
| Schema comes from | Function signature + docstring | Function signature + docstring |
| Simplest "let the LLM call it" call | `model.bind_tools([...]).invoke(...)` | `Settings.llm.predict_and_call([...], ...)` |
| Loops automatically? | No, one call | No, one call (`FunctionAgent`, Lesson 15, loops) |

## The code, piece by piece

```python
EXPENSE_LIMITS = {"meals": "50 EUR per day", ...}

def get_expense_limit(category: str) -> str:
    """Look up Nimbus Robotics' reimbursement limit for an expense category.

    Args:
        category: The expense category, e.g. "meals", "hotel", "flights", or "software".
    """
    ...
```

A plain Python function, nothing LlamaIndex-specific about it yet. It's a
hardcoded dict lookup, not a real API call, deterministic and free to run
repeatedly. The docstring matters: `FunctionTool` reads it to build the
tool's description and its parameter descriptions.

```python
expense_tool = FunctionTool.from_defaults(fn=get_expense_limit)
```

Wraps the function as a `FunctionTool`. Under the hood this inspects the
function's signature (name, parameter names, type annotations) and parses
its docstring (overall description, per-parameter descriptions) to build a
schema the LLM can read, the same "introspect a Python function into a
tool schema" idea as LangChain's `@tool` decorator, just written as a
classmethod call instead of a decorator.

```python
response = Settings.llm.predict_and_call([expense_tool], question, verbose=True)
```

`predict_and_call()` is the simplest tool-calling mechanism LlamaIndex
offers: one LLM call decides whether (and how) to call a tool from the
list, then LlamaIndex actually runs it, and the result comes back wrapped
in an `AgentChatResponse`. `verbose=True` prints each step (which function
was called, with what arguments, and what it returned) as it happens.
There's no loop, if the model wanted to call a second tool after seeing
the first result, this call wouldn't do that, it calls what the model asks
for in this single turn and returns.

```python
print(response.sources[0].content)
```

`response.sources` holds the raw `ToolOutput` objects produced along the
way, the tool's actual return value, separate from whatever the LLM chose
to phrase as its final answer.

## Running it

```bash
uv run python lessons/llamaindex/02_intermediate/14_tools_and_function_calling/lesson.py
```

## Expected output

Captured from a real run. Tool selection and phrasing are stable here
because the question only fits one tool and one category, but treat exact
wording as non-deterministic in general:

```
Tool built from a plain Python function:
  name: get_expense_limit
  description: get_expense_limit(category: str) -> str
Look up Nimbus Robotics' reimbursement limit for an expense category.

Args:
    category: The expense category, e.g. "meals", "hotel", "flights", or "software".
=== Calling Function ===
Calling function: get_expense_limit with args: {"category": "hotel"}
=== Function Output ===
The reimbursement limit for hotel is 150 EUR per night.

Question: What is Nimbus Robotics' reimbursement limit for hotel expenses?
Answer: The reimbursement limit for hotel is 150 EUR per night.

Raw tool output: The reimbursement limit for hotel is 150 EUR per night.
```

## Checkpoint

- **`FunctionTool.from_defaults(fn=...)`**: wraps a plain Python function
  as a tool, reading its signature and docstring to build the schema an
  LLM sees, LlamaIndex's equivalent of LangChain's `@tool` decorator.
- **`Settings.llm.predict_and_call([tools], question)`**: the simplest
  tool-calling call, one decision, one (optional) tool run, one result,
  no loop.
- `response.sources` holds the raw `ToolOutput`(s), the tool's actual
  return value, separate from the LLM's final phrasing.
- This is the building block Lesson 15's `FunctionAgent` loops on top of,
  a real agent is repeated rounds of this same decision.

If anything here still feels unclear, ask before moving to Lesson 15.
