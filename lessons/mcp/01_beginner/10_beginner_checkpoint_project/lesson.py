"""
Lesson 10 (Checkpoint): exercising the Notes Server end to end.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/01_beginner/10_beginner_checkpoint_project/lesson.py

This is the beginner tier's checkpoint: nothing here is a new concept,
it's tools, resources, prompts, error handling, and stdio-safe logging,
all from Lessons 2-8, combined into one server.
"""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = Path(__file__).parent / "server.py"


async def main() -> None:
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER_SCRIPT)])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            first_id = (await session.call_tool("add_note", {"text": "Buy milk."})).content
            second_id = (await session.call_tool("add_note", {"text": "Finish the MCP course."})).content
            print("Added notes:", first_id, second_id)

            notes = await session.call_tool("list_notes", {})
            print("\nAll notes:", notes.content)

            note = await session.read_resource("notes://1")
            print("\nnotes://1 ->", note.contents[0].text)

            prompt = await session.get_prompt("summarize_notes", {})
            print("\nsummarize_notes prompt:")
            print(" ", prompt.messages[0].content.text)

            deleted = await session.call_tool("delete_note", {"note_id": 1})
            print("\nDeleted note 1:", deleted.content)

            failed = await session.call_tool("delete_note", {"note_id": 999})
            print("\nDeleting a missing note, isError:", failed.isError)
            print(" ", failed.content)


if __name__ == "__main__":
    asyncio.run(main())
