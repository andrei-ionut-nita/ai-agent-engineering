# Lesson 7: Multi-Tool Agents

## Where we left off

Every lesson so far declared exactly one tool. This lesson adds a
second, deliberately unrelated one, `get_current_datetime()`, a
timezone lookup using Python's standard-library `zoneinfo`, no new
dependency. The point isn't the time tool itself, it's forcing the loop
to actually dispatch: given a call the model made, which of *several*
real functions does it correspond to?

## The code, piece by piece

```python
def get_current_datetime(timezone: str) -> str:
    try:
        tz = ZoneInfo(timezone)
    except Exception:
        return f"Unknown IANA timezone name: {timezone!r}"
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d %H:%M %Z")
```

Chosen specifically because it needs no new dependency (`zoneinfo` is
in the Python standard library) and has nothing to do with retrieval,
a clean second tool to prove the loop generalizes.

```python
TOOLS = types.Tool(
    function_declarations=[SEARCH_NOTES_DECLARATION, GET_CURRENT_DATETIME_DECLARATION]
)
```

One `Tool` can carry more than one `FunctionDeclaration`; Gemini sees
both and picks (at most) one per turn based on which one's description
best matches the question, exactly the same judgment Lesson 6 already
showed for the single-tool case, now with a real second option instead
of just "answer directly."

```python
def run_tool(call: types.FunctionCall, store: list[dict]) -> str:
    if call.name == "search_notes":
        return search_notes(call.args["query"], store)
    elif call.name == "get_current_datetime":
        return get_current_datetime(call.args["timezone"])
    else:
        raise ValueError(f"Unknown tool: {call.name}")
```

This is the new piece: a dispatch step between "the model requested a
call" and "run the matching Python function." With two tools it's a
two-branch `if/elif`, entirely readable. Hold onto that feeling, this
exact shape is what Lesson 19 revisits once a third and fourth tool
make it noticeably less pleasant.

## Running it

```bash
uv run python lessons/agentic_rag/01_beginner/07_multi_tool_agents/lesson.py
```

## Expected output

```
Q: What time is it right now in Tokyo?
A: <the current date and time in Asia/Tokyo>

Q: How often does Clarence the sourdough starter need feeding at room temperature?
A: Clarence needs feeding every 12 hours at room temperature.
```

The first answer's exact time depends on when you run it, that's
expected, `get_current_datetime()` is genuinely live.

## Checkpoint

- A single `Tool` can bundle multiple `FunctionDeclaration`s; the model
  picks which (if any) fits a given question.
- `run_tool()`'s `if/elif` dispatch, matching `call.name` to the real
  function, is the piece that grows with every new tool.
- The model's tool choice depends entirely on each tool's `description`
  being distinct enough to tell them apart, vague descriptions for two
  tools make wrong dispatch (right function, wrong reason, or the
  reverse) more likely.

If anything here still feels unclear, ask before moving to Lesson 8.
