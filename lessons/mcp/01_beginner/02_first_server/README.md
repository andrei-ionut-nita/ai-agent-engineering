# Lesson 2: Your first MCP server

## FastMCP: the high-level server API

The official Python MCP SDK ships a class called `FastMCP` that does
for servers what `@tool` did for LangChain functions: you write a
normal Python function, decorate it, and the SDK handles turning it
into something a client can discover and call.

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("calculator-server")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b
```

`FastMCP("calculator-server")` creates the server object. The string is
the server's name, this is what a host displays when it lists connected
servers, similar to how `calculator.name` was what an AI saw for a
LangChain tool.

## `@mcp.tool()` vs. `@tool`

If this looks almost identical to `@tool` from `langchain/13_defining_tools`,
that's the point. Both wrap a plain function so something else, an AI,
a client, can be told its name, description, and argument schema
without seeing the implementation. The difference is *where* that
description travels: `@tool` keeps it in the same Python process; `@mcp.tool()`
sends it over a protocol to a completely separate program.

## Running the server

A server needs a run loop. `mcp.run()` starts it and blocks, listening
for a client to connect:

```python
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

`transport="stdio"` means the server reads requests from standard input
and writes responses to standard output. That's the default for local
servers a host launches as a subprocess, more on this in Lesson 8, and
what every server in this course uses until Lesson 20.

## Running it

This server has no client yet, so running it directly will just sit
there waiting for stdio input, not very satisfying to watch. Instead,
`lesson.py` includes a small `main()` that calls the tool function
directly, the same trick `langchain/13_defining_tools` used, so you can
see the tool works before any protocol is involved:

```bash
uv run python lessons/mcp/01_beginner/02_first_server/lesson.py
```

In Lesson 9 you'll connect a real inspector to a server like this one
and see the actual protocol messages. In Lesson 11 you'll write a real
client. For now, focus on: what does `@mcp.tool()` turn a function
into?

## Checkpoint

- **`FastMCP`**: the high-level class for building an MCP server,
  imported from `mcp.server.fastmcp`.
- **`@mcp.tool()`**: decorates a function so it's exposed to clients,
  name/description/schema all pulled from the function itself.
- **`mcp.run(transport="stdio")`**: starts the server's request loop,
  reading/writing over standard input/output.
- A tool function still works as a plain function underneath, nothing
  about calling it directly has changed.

If anything here still feels unclear, ask before moving to Lesson 3,
where we look at exactly how that schema gets built.
