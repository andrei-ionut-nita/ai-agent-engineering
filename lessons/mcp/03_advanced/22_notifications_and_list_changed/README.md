# Lesson 22: A server announcing that its tools changed

## The problem this solves

Every client so far called `list_tools()` once, right after connecting,
and assumed that list stayed accurate for the whole conversation. A
server's tools aren't always static, though: a tool might unlock
another one, a permission might change, an integration might come
online partway through a session. Re-polling `list_tools()` on a timer
would work, but it's wasteful and slow to react. **Notifications** let
the server push a heads-up instead.

## A tool that changes the tool list

```python
@mcp.tool()
async def unlock_secret_tool(ctx: Context) -> str:
    """Unlock a hidden bonus tool."""
    def multiply(a: int, b: int) -> int:
        return a * b
    multiply.__doc__ = "Multiply two numbers."
    mcp.add_tool(multiply, name="multiply")
    await ctx.session.send_tool_list_changed()
    return "Unlocked the multiply tool!"
```

`mcp.add_tool(fn, name=...)` registers a new tool at runtime, the
programmatic version of decorating a function with `@mcp.tool()` at
import time. Adding it doesn't announce it by itself, that's what
`ctx.session.send_tool_list_changed()` does: it sends a
`notifications/tools/list_changed` message, no response expected, to
whichever client is currently connected.

## Receiving it on the client

A `ClientSession` accepts a `message_handler`, a callback invoked for
every notification (and out-of-band message) that arrives outside the
normal request/response flow:

```python
notifications_seen = []


async def message_handler(message):
    notifications_seen.append(message)


async with ClientSession(read, write, message_handler=message_handler) as session:
    ...
```

Call `unlock_secret_tool`, and shortly after, `message_handler` fires
with a `ServerNotification` wrapping a `ToolListChangedNotification`.
The correct reaction, the same one a real host would take, is to call
`list_tools()` again rather than trust the stale list from before.

## Why this needs to be explicit

Notice `mcp.add_tool()` alone did *not* trigger anything, the server
had to call `send_tool_list_changed()` itself. MCP's notification
system is opt-in and best-effort on both sides: a server chooses when
a change is worth announcing, and a client isn't guaranteed to receive
every notification (say, across a reconnect), so a well-behaved client
still refreshes periodically rather than relying on notifications
alone.

## Running it

```bash
uv run python lessons/mcp/03_advanced/22_notifications_and_list_changed/lesson.py
```

## Checkpoint

- **`mcp.add_tool(fn, name=...)`**: registers a tool at runtime, same
  registration `@mcp.tool()` does at import time.
- **`ctx.session.send_tool_list_changed()`**: explicitly announces a
  change, this does not happen automatically.
- **`message_handler`**: a `ClientSession` callback for notifications
  arriving outside the normal request/response flow.
- Notifications are a best-effort heads-up, not a replacement for
  occasionally re-checking `list_tools()`.

If anything here still feels unclear, ask before moving to Lesson 23,
a server asking the user a question mid-call.
