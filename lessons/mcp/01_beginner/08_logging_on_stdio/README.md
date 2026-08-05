# Lesson 8: Why `print()` breaks a stdio server

## stdout is the protocol, not your console

Every server so far has used the stdio transport: the server reads
JSON-RPC requests from standard input and writes JSON-RPC responses to
standard output. That means standard output isn't a place to leave
yourself debug messages anymore, it's the wire the protocol runs on. A
stray `print()` inside a tool writes plain text onto the exact same
stream the client is trying to parse as JSON, one message per line.

## Watching it actually break

`bad_server.py` in this folder does exactly the wrong thing:

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    print("Processing request", flush=True)  # corrupts stdio!
    return a + b
```

Connect to it and call the tool, and the client's stdout reader tries
to parse `"Processing request"` as a JSON-RPC message and fails:

```
Failed to parse JSONRPC message from server
pydantic_core._pydantic_core.ValidationError: 1 validation error for JSONRPCMessage
  Invalid JSON: expected value at line 1 column 1 [type=json_invalid, input_value='Processing request', ...]
```

In this lesson the bad line lands on its own, so the client logs the
parse failure and recovers on the next line. In a real server, a print
statement could just as easily land in the middle of a JSON line, or
push a response's bytes out of order, corrupting the message beyond
recovery and hanging the connection. Lucky timing here doesn't make it
safe.

## The fix: log to stderr, not stdout

`good_server.py` does the same job with the standard library `logging`
module instead:

```python
import logging

logger = logging.getLogger(__name__)


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    logger.info("Processing request")  # writes to stderr, safe
    return a + b
```

`logging`'s default handler writes to `stderr`, a completely separate
stream from the one carrying JSON-RPC traffic. The client never sees
these lines at all, run this server and the same tool call succeeds
with no parse warning.

## The rule, and its one exception

**Never call `print()` inside a stdio MCP server.** Use `logging`
instead, one logger per module (`logging.getLogger(__name__)`), same
convention as any other Python service. This rule is specific to the
stdio transport: an HTTP-based server (Lesson 20) can log to stdout
freely, because HTTP responses don't share a stream with your terminal
output the way stdio does.

## Running it

```bash
uv run python lessons/mcp/01_beginner/08_logging_on_stdio/lesson.py
```

## Checkpoint

- On the stdio transport, standard output *is* the protocol, anything
  written there that isn't a JSON-RPC message corrupts the stream.
- `print()` inside a stdio server's tool is a real, demonstrable bug,
  not just a style nitpick.
- Use `logging.getLogger(__name__)`, which writes to stderr by default,
  for any debug output inside a stdio server.
- This restriction is specific to stdio; HTTP-based servers (Lesson 20)
  can log to stdout normally.

If anything here still feels unclear, ask before moving to Lesson 9,
the MCP Inspector.
