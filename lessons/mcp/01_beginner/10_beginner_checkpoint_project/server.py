"""
Beginner checkpoint: a Notes Server combining tools, resources,
prompts, error handling, and stderr-safe logging, one server per
concept taught in Lessons 2-8.
"""

import logging

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)
mcp = FastMCP("notes-server")

_notes: dict[int, str] = {}
_next_id = 1


@mcp.tool()
def add_note(text: str) -> int:
    """Add a note and return its id."""
    global _next_id
    note_id = _next_id
    _notes[note_id] = text
    _next_id += 1
    logger.info("Added note %s", note_id)
    return note_id


@mcp.tool()
def list_notes() -> dict[int, str]:
    """List every note currently stored, by id."""
    return dict(_notes)


@mcp.tool()
def delete_note(note_id: int) -> str:
    """Delete a note by id."""
    if note_id not in _notes:
        raise ValueError(f"No note with id {note_id}.")
    del _notes[note_id]
    logger.info("Deleted note %s", note_id)
    return f"Deleted note {note_id}."


@mcp.resource("notes://{note_id}")
def read_note(note_id: str) -> str:
    """Read a single note's content by id."""
    parsed_id = int(note_id)
    if parsed_id not in _notes:
        return f"No note with id {parsed_id}."
    return _notes[parsed_id]


@mcp.prompt()
def summarize_notes() -> str:
    """Ask a model to summarize every note currently stored."""
    if not _notes:
        return "There are no notes yet."
    joined = "\n".join(f"- {text}" for text in _notes.values())
    return f"Please summarize these notes in two sentences:\n\n{joined}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
