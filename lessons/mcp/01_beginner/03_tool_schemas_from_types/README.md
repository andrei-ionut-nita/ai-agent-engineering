# Lesson 3: How a schema gets built from your function

## What the client actually sees

In `langchain/13_defining_tools`, the checkpoint was: "the AI will
never see the actual implementation, only a name, a description, and
an argument schema." The exact same is true here, an MCP client never
sees `add`'s Python source, it only sees whatever `tools/list` reports.

Let's look at what that is:

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b
```

Calling `await mcp.list_tools()` on the server directly, no client
needed yet, this function produces:

```python
name = "add"
description = "Add two numbers together."
inputSchema = {
    "type": "object",
    "properties": {
        "a": {"title": "A", "type": "integer"},
        "b": {"title": "B", "type": "integer"},
    },
    "required": ["a", "b"],
}
```

## Where each piece comes from

- **`name`**: the function's name, `add`, unless you pass `@mcp.tool(name="...")`.
- **`description`**: the docstring, word for word. This is not a
  comment for humans anymore, once it leaves your process it is the
  entire instruction manual an AI has to work with, exactly the same
  lesson from `langchain/13_defining_tools`.
- **`inputSchema`**: built from the function's type hints. `a: int`
  becomes `{"type": "integer"}`. FastMCP inspects the signature at
  decoration time and generates a JSON Schema automatically, you never
  write the schema by hand.

## Why this matters more here than in LangChain

In LangChain, a bad docstring produces a confused local AI call, you'll
notice quickly because it's all in one process. Here, the description
and schema are what's sent across a wire to a completely different
program, possibly one you don't control and can't easily debug. A vague
description or a missing type hint is now a silent contract failure
between two systems, not a bug you'll trip over immediately.

## Optional parameters and defaults

Give a parameter a default value and it becomes optional in the schema:

```python
@mcp.tool()
def add(a: int, b: int = 0) -> int:
    """Add two numbers, b defaults to 0 if omitted."""
    return a + b
```

Now `required` only lists `"a"`. `lesson.py` shows both versions side
by side.

## Running it

```bash
uv run python lessons/mcp/01_beginner/03_tool_schemas_from_types/lesson.py
```

## Checkpoint

- **`inputSchema`**: a JSON Schema, generated from your function's type
  hints, that tells a client exactly what arguments a tool expects.
- **`description`**: your docstring, sent verbatim, the only "documentation"
  an AI on the other end will ever see.
- Default values make a parameter optional in the generated schema.
- `await mcp.list_tools()` lets you inspect exactly what a client would
  see, without needing a client yet.

If anything here still feels unclear, ask before moving to Lesson 4,
where we add more than one tool to the same server.
