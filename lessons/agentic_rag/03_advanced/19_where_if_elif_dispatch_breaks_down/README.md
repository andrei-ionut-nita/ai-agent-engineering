# Lesson 19: Where if/elif Dispatch Breaks Down

## Where we left off

Every lesson since Lesson 7 dispatched tool calls with a two-branch
`if/elif`, perfectly readable at that size. This lesson adds a third
tool, `calculate()`, a trivial arithmetic evaluator, and deliberately
demonstrates the specific way `if/elif` dispatch breaks as a toolset
grows: not by getting slower or uglier, but by silently *decoupling*
two things that need to stay in sync, which tools are declared to the
model, and which tools the dispatch code actually knows how to run.

## The code, piece by piece

```python
TOOLS = types.Tool(
    function_declarations=[SEARCH_NOTES_DECLARATION, GET_CURRENT_DATETIME_DECLARATION, CALCULATE_DECLARATION]
)
```

All three tools are declared to the model, `calculate` included. The
model can, and will, request it for an arithmetic question.

```python
def run_tool_incomplete(call: types.FunctionCall, store: list[dict]) -> str:
    if call.name == "search_notes":
        return search_notes(call.args["query"], store)
    elif call.name == "get_current_datetime":
        return get_current_datetime(call.args["timezone"])
    else:
        raise ValueError(f"Unknown tool: {call.name}")
```

The dispatch function was never updated to match. This isn't a
contrived typo, it's what actually happens in a growing codebase: the
`Tool` declaration list lives in one place, the `if/elif` chain lives
in another, and adding a tool to one without remembering the other
produces code that still compiles, still runs, still answers most
questions correctly, right up until a question needs specifically the
tool whose branch got missed.

## Why this is worse than it looks

The failure here isn't just "one more line to remember." It's that
**nothing in the code's structure enforces the connection** between
declared tools and dispatchable tools. A `Tool` list and an `if/elif`
chain are two independent pieces of Python with no shared source of
truth; keeping them in sync is a discipline you have to maintain by
hand, and that discipline gets harder, not easier, as the number of
tools grows, exactly backwards from what you'd want. This is the same
class of problem Lesson 16 called a "malformed tool call" failure, a
call the model made in good faith that the runtime side can't fulfill,
except here the runtime side, not the model, is what's actually
malformed.

## Running it

```bash
uv run python lessons/agentic_rag/03_advanced/19_where_if_elif_dispatch_breaks_down/lesson.py
```

## Expected output

```
Q: What is 240 divided by 4?

Three tools are declared to the model (search_notes, get_current_datetime,
calculate), but run_tool_incomplete()'s if/elif chain only handles the
first two, calculate's declaration exists, but nothing wires it to the
real calculate() function above.

Crashed: Unknown tool: calculate

This is exactly the bug a growing if/elif chain invites: ...
```

## Checkpoint

- Declaring a tool to the model and wiring its dispatch are two
  separate steps, in two separate places, with nothing connecting them.
- That gap doesn't show up in testing until a question specifically
  needs the missing tool, making it easy to ship undetected.
- A single, unified data structure, one thing that both declares a
  tool to the model AND knows how to run it, would make this class of
  bug structurally impossible instead of merely avoidable with care.
  That structure, a tool registry, is Lesson 21.

If anything here still feels unclear, ask before moving to Lesson 20.
