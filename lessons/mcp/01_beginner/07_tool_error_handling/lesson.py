"""
Lesson 7: a raised exception becomes an error result, not a crash.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/01_beginner/07_tool_error_handling/lesson.py

This is the first lesson with a real client and server as two separate
processes: server.py runs in its own subprocess, and this file connects
to it over stdio, the same shape every lesson from Lesson 11 onward
uses.
"""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = Path(__file__).parent / "server.py"


async def main() -> None:
    # StdioServerParameters describes the subprocess to launch: which
    # interpreter, which script. sys.executable ensures we use the same
    # Python (and uv-managed virtualenv) this lesson is running under.
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER_SCRIPT)])

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            # The handshake: protocol version and capabilities are
            # negotiated here, before any other request is allowed.
            await session.initialize()

            failing = await session.call_tool("divide", {"a": 10, "b": 0})
            print("Dividing by zero:")
            print("  isError:", failing.isError)
            print("  content:", failing.content)

            succeeding = await session.call_tool("divide", {"a": 10, "b": 2})
            print("\nDividing normally:")
            print("  isError:", succeeding.isError)
            print("  content:", succeeding.content)


if __name__ == "__main__":
    asyncio.run(main())
