# Lesson 21: A Tool Registry Pattern

## Where we left off

Lesson 19 diagnosed the actual disease: a declared-tools list and a
dispatch chain, kept in sync only by discipline. Lesson 20 separated
loop mechanics from tool knowledge but didn't touch that disease, the
`if/elif` (renamed `make_dispatch`) was still one hand-maintained
list living apart from another. This lesson replaces both with a
single data structure that makes the bug structurally impossible, not
just easier to avoid.

## The code, piece by piece

```python
@dataclass
class Tool:
    declaration: types.FunctionDeclaration
    fn: Callable[..., str]
```

The core idea in three lines: a tool's declaration (what the model
sees) and its function (what actually runs) live in the *same object*.
There is no way to create a `Tool` with one and not the other, the
`dataclass` requires both.

```python
def build_registry(store: list[dict]) -> dict[str, Tool]:
    return {
        "search_notes": Tool(declaration=..., fn=lambda query: search_notes(query, store)),
        "get_current_datetime": Tool(declaration=..., fn=get_current_datetime),
        "calculate": Tool(declaration=..., fn=calculate),
    }
```

One dict, keyed by tool name, three entries, `calculate()` (this
lesson's new, third tool, a safe `ast`-based arithmetic evaluator, no
`eval()`/`exec()`, no new dependency) included from the start, with
nothing separate to remember.

```python
declarations = [tool.declaration for tool in registry.values()]
config = types.GenerateContentConfig(tools=[types.Tool(function_declarations=declarations)])
```

`run_agent()` builds the model-facing `Tool` list *from* the registry,
every single time, rather than from a separately maintained constant.
There is no longer a second list that could drift out of sync, the
registry is the only list.

```python
def dispatch(call: types.FunctionCall, registry: dict[str, Tool]) -> dict[str, str]:
    tool = registry.get(call.name)
    if tool is None:
        return {"error": f"Unknown tool: {call.name}"}
    try:
        return {"output": tool.fn(**(call.args or {}))}
    ...
```

Dispatch is now a dict lookup, not a chain of comparisons, `registry.get(call.name)`
either finds a fully-formed `Tool` (declaration and function both
guaranteed present) or it doesn't, in which case the error path is the
*only* remaining way this can fail, not a symptom of two lists falling
out of sync.

## Why this is a different kind of fix than Lesson 20's

Lesson 20 was an organizational improvement, code got easier to read
and reuse, but the same bug was still possible to write. This lesson is
a structural one: Lesson 19's exact failure (a declared tool with no
matching dispatch branch) cannot be expressed in this data structure at
all. That distinction, "harder to get wrong" versus "impossible to get
wrong in this specific way," is worth noticing generally: the strongest
fix for a class of bug is usually a data structure that makes the bug
unrepresentable, not a reminder to be more careful.

## Running it

```bash
uv run python lessons/agentic_rag/03_advanced/21_a_tool_registry_pattern/lesson.py
```

## Expected output

```
Q: What is 240 divided by 4?
A: 60.0

Q: How often does the sourdough starter need feeding at room temperature?
A: The sourdough starter needs feeding every 12 hours at room temperature.

Q: What time is it right now in Tokyo?
A: <the current date and time in Asia/Tokyo>

Registry has 3 tools: ['calculate', 'get_current_datetime', 'search_notes']. Adding a fourth would mean adding one more Tool(...) entry to build_registry(), nothing else, Lesson 19's forgotten-branch bug isn't just avoided here, it's not expressible in this structure at all.
```

## Checkpoint

- **`Tool` (dataclass)**: bundles a `FunctionDeclaration` with its real
  callable, one object instead of two lists to keep in sync.
- **registry**: `dict[str, Tool]`, the single source of truth for both
  "what's declared to the model" and "what can actually run."
- Adding a tool now means adding one dict entry, no separate dispatch
  branch to remember.
- **Try this yourself**: add a fourth tool of your own to
  `build_registry()` (reuse Lesson 9's word-counter or converter idea
  if you built one). Confirm it works with a targeted question, then
  count how many places in the file you had to touch. Compare that to
  how many places Lesson 19's version would have needed.

If anything here still feels unclear, ask before moving to Lesson 22.
