"""
Lesson 12: calling a tool, and reading what comes back.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/02_intermediate/12_calling_tools_from_a_client/lesson.py
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

            result = await session.call_tool("add", {"a": 2, "b": 3})
            print("A correct call:")
            print("  isError:", result.isError)
            print("  content:", result.content)
            print("  structuredContent:", result.structuredContent)

            # Deliberately calling with a missing required argument, to
            # see what a schema-validation failure looks like from the
            # client's side. Notice this does not raise, isError just
            # comes back True, same as Lesson 7's exception-in-a-tool.
            bad_result = await session.call_tool("add", {"a": 2})
            print("\nA call missing the 'b' argument:")
            print("  isError:", bad_result.isError)
            print("  content:", bad_result.content)


if __name__ == "__main__":
    asyncio.run(main())
