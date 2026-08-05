# Lesson 18: Server-side state shared across calls

## The problem module-level state doesn't solve well

The beginner checkpoint's Notes Server (Lesson 10) kept its notes in a
plain module-level dict. That works, but it can't run any setup before
the first request or cleanup after the last one, no opening a database
connection at startup and closing it at shutdown. That's what a
**lifespan** is for.

## Defining a lifespan

```python
from contextlib import asynccontextmanager
from dataclasses import dataclass
from collections.abc import AsyncIterator

from mcp.server.fastmcp import FastMCP, Context


@dataclass
class AppState:
    connection_count: int = 0


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[AppState]:
    logger.info("startup")          # e.g. open a DB connection here
    state = AppState()
    try:
        yield state
    finally:
        logger.info("shutdown")     # e.g. close it here

mcp = FastMCP("lifespan-demo", lifespan=lifespan)
```

Whatever the lifespan `yield`s becomes the server's shared app state,
created once when the server starts, torn down once when it stops,
identical in shape to a pytest fixture or a FastAPI lifespan, if you've
used either.

## Reaching that state from a tool

A tool asks for it by adding a `Context` parameter to its signature:

```python
@mcp.tool()
def ping(ctx: Context) -> str:
    """Increment and report the connection count."""
    state: AppState = ctx.request_context.lifespan_context
    state.connection_count += 1
    return f"pinged {state.connection_count} times"
```

FastMCP recognizes the `Context` type hint and injects it
automatically, a tool doesn't declare `ctx` as part of the schema a
client sees (compare Lesson 3, this parameter is invisible to
`inputSchema`), it's purely a server-side detail. Call `ping` twice in
the same connection and `connection_count` climbs, `1`, then `2`,
proving the state genuinely persists between calls rather than
resetting each time.

## Where this replaces the beginner checkpoint's approach

The Notes Server's module-level `_notes` dict works for a lesson, but
it's global mutable state with no setup/teardown hook and no clean way
to, say, swap in a real database connection later. A production server
would define `AppState` with a real connection pool, open it in the
lifespan, and reach it through `Context` in every tool, exactly this
shape, just with more realistic contents.

## Running it

```bash
uv run python lessons/mcp/02_intermediate/18_lifespan_and_app_context/lesson.py
```

## Checkpoint

- **`lifespan`**: an async context manager passed to `FastMCP(...)`,
  runs setup before the first request and teardown after the last.
- Whatever it `yield`s becomes shared app state for the server's
  lifetime.
- **`Context`**: a tool parameter FastMCP injects automatically, giving
  access to `ctx.request_context.lifespan_context`, invisible to the
  client-facing schema.
- This replaces ad hoc module-level globals (Lesson 10's approach) with
  a real setup/teardown lifecycle.

If anything here still feels unclear, ask before moving to Lesson 19,
the intermediate checkpoint project.
