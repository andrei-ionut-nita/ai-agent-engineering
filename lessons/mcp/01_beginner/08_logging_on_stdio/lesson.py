"""
Lesson 8: why print() breaks a stdio server, and the logging fix.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/01_beginner/08_logging_on_stdio/lesson.py

This connects to bad_server.py first, expect to see a JSON parse
warning printed by the client's stdio reader, then to good_server.py,
which produces no such warning.
"""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = Path(__file__).parent


async def call_add(server_script: Path) -> None:
    params = StdioServerParameters(command=sys.executable, args=[str(server_script)])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("add", {"a": 2, "b": 3})
            print("  result:", result.content)


async def main() -> None:
    print("Calling bad_server.py (uses print(), watch stderr for a parse warning):")
    await call_add(HERE / "bad_server.py")

    print("\nCalling good_server.py (uses logging, no parse warning):")
    await call_add(HERE / "good_server.py")


if __name__ == "__main__":
    asyncio.run(main())
