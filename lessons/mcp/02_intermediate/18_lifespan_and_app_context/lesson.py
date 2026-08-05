"""
Lesson 18: server-side state shared across calls via lifespan + Context.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/02_intermediate/18_lifespan_and_app_context/lesson.py
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

            # Same connection, three calls: the count climbs each time,
            # proving AppState survives between requests instead of
            # resetting.
            for _ in range(3):
                result = await session.call_tool("ping", {})
                print(result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
