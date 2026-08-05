"""
Lesson 23: elicitation, a server asking the user a question mid-call.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/03_advanced/23_elicitation/lesson.py
"""

import asyncio
import sys
from pathlib import Path

import mcp.types as types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = Path(__file__).parent / "server.py"


async def accepting_callback(context, params: types.ElicitRequestParams):
    print("  [server asks]:", params.message, "-> answering: confirm=True")
    return types.ElicitResult(action="accept", content={"confirm": True})


async def declining_callback(context, params: types.ElicitRequestParams):
    print("  [server asks]:", params.message, "-> answering: decline")
    return types.ElicitResult(action="decline")


async def run_with(label: str, callback) -> None:
    print(f"{label}:")
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER_SCRIPT)])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write, elicitation_callback=callback) as session:
            await session.initialize()
            result = await session.call_tool("delete_file", {"filename": "notes.txt"})
            print("  result:", result.content)


async def main() -> None:
    await run_with("A client that accepts", accepting_callback)
    print()
    await run_with("A client that declines", declining_callback)


if __name__ == "__main__":
    asyncio.run(main())
