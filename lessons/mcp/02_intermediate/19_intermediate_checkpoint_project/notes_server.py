"""
Intermediate checkpoint: a notes server using lifespan-managed state
(Lesson 18) instead of the beginner checkpoint's module-level dict.
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field

from mcp.server.fastmcp import Context, FastMCP

logger = logging.getLogger(__name__)


@dataclass
class NotesState:
    notes: dict[int, str] = field(default_factory=dict)
    next_id: int = 1


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[NotesState]:
    logger.info("Notes server starting up")
    yield NotesState()
    logger.info("Notes server shutting down")


mcp = FastMCP("notes-server", lifespan=lifespan)


@mcp.tool()
def add_note(text: str, ctx: Context) -> int:
    """Add a note and return its id."""
    state: NotesState = ctx.request_context.lifespan_context
    note_id = state.next_id
    state.notes[note_id] = text
    state.next_id += 1
    return note_id


@mcp.tool()
def list_notes(ctx: Context) -> dict[int, str]:
    """List every note currently stored, by id."""
    state: NotesState = ctx.request_context.lifespan_context
    return dict(state.notes)


if __name__ == "__main__":
    mcp.run(transport="stdio")
