"""
Lesson 5: resources, read-only context instead of actions.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/01_beginner/05_resources/lesson.py
"""

import asyncio

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("notes-server")


@mcp.resource("notes://today")
def today_note() -> str:
    """Today's note."""
    return "Buy milk."


@mcp.resource("notes://{date}")
def note_for_date(date: str) -> str:
    """Get the note for a given date."""
    return f"Note for {date}: nothing recorded yet."


async def main() -> None:
    resources = await mcp.list_resources()
    print("Registered resources:")
    for resource in resources:
        print(f"  {resource.uri}: {resource.description}")

    fixed = await mcp.read_resource("notes://today")
    print("\nnotes://today ->", fixed[0].content)

    # notes://{date} is a template: any date-shaped URI routes here,
    # with `date` filled in from the URI itself.
    templated = await mcp.read_resource("notes://2026-08-03")
    print("notes://2026-08-03 ->", templated[0].content)


if __name__ == "__main__":
    asyncio.run(main())
