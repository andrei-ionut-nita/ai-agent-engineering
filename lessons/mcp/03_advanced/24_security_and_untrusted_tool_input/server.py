"""
The server half of Lesson 24: a vulnerable tool and its fixed
counterpart, side by side, so lesson.py can demonstrate both.
"""

from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("security-demo-server")

NOTES_DIR = (Path(__file__).parent / "data").resolve()


@mcp.tool()
def read_note_unsafe(filename: str) -> str:
    """Read a note file by name (no path validation, do not copy this)."""
    path = NOTES_DIR / filename
    return path.read_text()


@mcp.tool()
def read_note_safe(filename: str) -> str:
    """Read a note file by name, rejecting paths outside the notes directory."""
    candidate = (NOTES_DIR / filename).resolve()
    if not candidate.is_relative_to(NOTES_DIR):
        raise ValueError(f"'{filename}' is outside the notes directory.")
    return candidate.read_text()


if __name__ == "__main__":
    mcp.run(transport="stdio")
