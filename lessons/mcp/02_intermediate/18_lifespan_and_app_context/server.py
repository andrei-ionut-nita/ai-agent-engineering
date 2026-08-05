"""The server half of Lesson 18: shared state via lifespan + Context."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import Context, FastMCP

logger = logging.getLogger(__name__)


@dataclass
class AppState:
    connection_count: int = 0


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[AppState]:
    # In a real server, this is where you'd open a database connection
    # or a client for some external API.
    logger.info("Server starting up")
    state = AppState()
    try:
        yield state
    finally:
        # And this is where you'd close it.
        logger.info("Server shutting down")


mcp = FastMCP("lifespan-demo-server", lifespan=lifespan)


@mcp.tool()
def ping(ctx: Context) -> str:
    """Increment and report how many times this server has been pinged."""
    state: AppState = ctx.request_context.lifespan_context
    state.connection_count += 1
    return f"pinged {state.connection_count} times"


if __name__ == "__main__":
    mcp.run(transport="stdio")
