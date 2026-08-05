# Lesson 20: Running a server over HTTP instead of stdio

## Same protocol, different pipe

Every server through Lesson 19 used the stdio transport: a subprocess
your own script launched, one client per process. That only works for
a server running on the same machine as its client. The **Streamable
HTTP transport** is MCP's answer for a server that needs to live
somewhere else entirely, and serve many clients at once, exactly the
Sentry-server example from Lesson 1's host/client/server picture.

Nothing about tools, resources, or prompts changes. The only thing
that changes is how a client and server exchange the same JSON-RPC
messages.

## Running a server over HTTP

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("http-demo-server", stateless_http=True, port=8931)


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

The only differences from every earlier server: `transport="streamable-http"`
instead of `"stdio"`, and a `port` to listen on. `stateless_http=True`
means the server doesn't keep session state tied to a specific
connection, appropriate for a demo like this one; a stateful server
(the default) can track per-client session data across requests, more
useful for something like Lesson 18's app state scoped to one
connected client rather than shared globally.

Run it and it behaves like any other web server, staying up and
listening until you stop it, unlike a stdio server, which a host
launches and tears down around a single client's lifetime.

## Connecting a client over HTTP

```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async with streamablehttp_client("http://127.0.0.1:8931/mcp") as (read, write, _):
    async with ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool("add", {"a": 4, "b": 5})
```

Compare this to Lesson 11's `stdio_client`: same `ClientSession`, same
`initialize()`/`call_tool()` calls, only the connection function and
its argument (a URL instead of `StdioServerParameters`) changed. This
is the payoff of MCP separating a transport layer from a data layer
back in Lesson 1: everything you already know how to do with a session
carries over unchanged.

## Running it

This lesson runs the server as a background process for the duration
of the script, then connects to it and shuts it down when done, so
there's nothing left running afterward.

```bash
uv run python lessons/mcp/03_advanced/20_streamable_http_transport/lesson.py
```

## Checkpoint

- **`transport="streamable-http"`**: runs a server as a long-lived HTTP
  service instead of a stdio subprocess.
- **`streamablehttp_client(url)`**: the HTTP equivalent of
  `stdio_client`, same `ClientSession` on the other side.
- Everything above the transport layer, tools, resources, prompts,
  `ClientSession`'s methods, is identical between stdio and HTTP.
- A stdio server's lifetime is tied to one client's connection; an
  HTTP server stays up and can serve many clients.

If anything here still feels unclear, ask before moving to Lesson 21,
adding authentication to that HTTP server.
