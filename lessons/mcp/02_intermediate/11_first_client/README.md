# Lesson 11: Your first MCP client

## What you already know

This is less new material than it looks like. Lesson 7 connected a
client to a server to watch error handling; Lesson 9 did it again to
compare against the Inspector; Lesson 10's checkpoint did it a third
time against your own Notes Server. This lesson just slows that same
shape down and explains every piece.

## The three layers of a connection

```python
params = StdioServerParameters(command=sys.executable, args=[str(server_script)])

async with stdio_client(params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()
```

- **`StdioServerParameters`**: configuration only, not a connection.
  Just describes which command to run and with what arguments.
- **`stdio_client(params)`**: an async context manager that launches
  the server as a subprocess and gives you back a `(read, write)`
  stream pair. Entering it starts the process; leaving it terminates
  it.
- **`ClientSession(read, write)`**: wraps those raw streams with the
  actual protocol logic: building JSON-RPC requests, matching
  responses by id, tracking capabilities.

## `session.initialize()` is not optional

Before any other request, the client and server perform a handshake:
the client declares its protocol version and capabilities, the server
responds with its own. `session.server_capabilities` and
`session.server_info` are populated by this call, and other requests
will fail if you skip it. This is the client-side mirror of
`server/discover` from Lesson 1's JSON-RPC sketch.

## Listing tools

```python
tools = await session.list_tools()
for tool in tools.tools:
    print(tool.name, tool.description)
```

`tools.tools` is a plain list of the same `Tool` objects you inspected
server-side with `mcp.list_tools()` back in Lesson 3, name,
description, `inputSchema`, just arriving from across the connection
this time instead of from the same process.

## Running it

`lesson.py` connects to `server.py` (a small server built just for
this lesson) and prints its declared capabilities and tool list.

```bash
uv run python lessons/mcp/02_intermediate/11_first_client/lesson.py
```

## Checkpoint

- **`StdioServerParameters`**: describes the subprocess to launch, not
  a live connection.
- **`stdio_client`**: launches the subprocess, gives you raw streams.
- **`ClientSession`**: the actual protocol logic, built on top of those
  streams.
- **`session.initialize()`**: the required handshake, must happen
  before any other request.
- **`session.list_tools()`**: returns the same `Tool` metadata you
  first saw generated server-side back in Lesson 3.

If anything here still feels unclear, ask before moving to Lesson 12,
actually calling one of these tools.
