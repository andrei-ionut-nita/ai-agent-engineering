# Lesson 4: Several tools on one server

## One server, many capabilities

Nothing stops a server from exposing more than one tool. Each
`@mcp.tool()` call registers another entry on the same `mcp` object:

```python
mcp = FastMCP("kitchen-server")


@mcp.tool()
def convert_celsius_to_fahrenheit(celsius: float) -> float:
    """Convert a Celsius temperature to Fahrenheit."""
    return celsius * 9 / 5 + 32


@mcp.tool()
def convert_cups_to_milliliters(cups: float) -> float:
    """Convert a volume in US cups to milliliters."""
    return cups * 236.588
```

`tools/list` now returns both. A client, or eventually an AI deciding
which one to use, sees two distinct entries, each with its own name,
description, and schema. Exactly like `langchain/15_multiple_tools`,
just server-hosted.

## Naming matters more here

In LangChain, tool names only needed to be unique within one Python
process. An MCP server might eventually run alongside other servers in
the same host (Lesson 17 covers this directly), so vague names like
`convert` or `get` become a real problem: which server's `convert` did
the AI mean? Prefer specific, descriptive names, `convert_celsius_to_fahrenheit`
rather than `convert`, the same way the official docs name their
example tools `get_alerts` and `get_forecast` rather than just `alerts`
and `forecast`.

## Running it

```bash
uv run python lessons/mcp/01_beginner/04_multiple_tools/lesson.py
```

## Checkpoint

- Multiple `@mcp.tool()` functions can live on the same `FastMCP`
  instance, each independently discoverable.
- `tools/list` (here, `await mcp.list_tools()`) returns all of them at
  once.
- Specific tool names matter more in MCP than in a single-process
  LangChain app, because a host may have several servers' tools mixed
  together.

If anything here still feels unclear, ask before moving to Lesson 5,
where we expose data instead of actions.
