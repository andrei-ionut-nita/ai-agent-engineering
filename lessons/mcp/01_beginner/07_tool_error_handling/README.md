# Lesson 7: A tool that fails, without crashing the server

## Raising is fine, actually

In LangChain, `langchain/16_tool_error_handling` taught you to catch
exceptions inside a tool and return an error string, because a raised
exception would blow up your whole process. MCP's story is different:
you're allowed to just `raise`.

```python
@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b
```

The MCP SDK catches this for you at the protocol boundary and turns it
into a *result*, not a crash: the response comes back with `isError=True`
and the error message as the content, and the server keeps running,
ready for the next call.

```python
result = await session.call_tool("divide", {"a": 10, "b": 0})
# result.isError == True
# result.content == [TextContent(text="Error executing tool divide: Cannot divide by zero.")]
```

## Why this needs a real client this time

Every earlier lesson called the tool function directly, or used
`mcp.list_tools()`/`mcp.call_tool()` in the same process. Watching a
raised exception turn into an `isError` result specifically requires
going through the real protocol boundary: a server running in its own
subprocess, talked to over stdio. This lesson introduces that shape
early, in miniature, so Lesson 11 doesn't feel like new machinery, it'll
just be *this*, generalized.

```python
params = StdioServerParameters(command="python", args=[server_script_path])
async with stdio_client(params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool("divide", {"a": 10, "b": 0})
```

`stdio_client` launches the server script as a subprocess and gives you
back a pair of streams. `ClientSession` wraps those streams with the
actual JSON-RPC protocol logic. `session.initialize()` performs the
handshake (protocol version, capabilities) before any other request is
allowed.

## `is_error`, not an exception, on the client side too

Notice the client doesn't need a `try`/`except` either. `call_tool`
always returns a `CallToolResult`, check `.isError` to see whether the
tool succeeded, the same pattern `langchain/16_tool_error_handling`
used for a failing tool call, just without needing to catch anything.

## Running it

```bash
uv run python lessons/mcp/01_beginner/07_tool_error_handling/lesson.py
```

## Checkpoint

- Raising a normal Python exception inside an `@mcp.tool()` function is
  the correct way to signal failure, the SDK converts it for you.
- The failure arrives as `CallToolResult(isError=True, content=[...])`,
  never as an exception the client has to catch.
- `stdio_client` + `ClientSession` + `session.initialize()` is the real
  connection shape every later client lesson builds on.

If anything here still feels unclear, ask before moving to Lesson 8,
why `print()` breaks a stdio server.
