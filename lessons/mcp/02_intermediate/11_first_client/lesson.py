"""
Lesson 11: the three layers of a client connection, explained slowly.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/02_intermediate/11_first_client/lesson.py
"""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = Path(__file__).parent / "server.py"


async def main() -> None:
    # Layer 1: configuration. No process has been started yet.
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER_SCRIPT)])

    # Layer 2: stdio_client launches the subprocess and hands back raw
    # (read, write) streams, entering the `async with` starts the
    # server, leaving it terminates it.
    async with stdio_client(params) as (read, write):
        # Layer 3: ClientSession wraps those streams with the real
        # JSON-RPC protocol logic.
        async with ClientSession(read, write) as session:
            # The handshake. Nothing else is valid before this.
            init_result = await session.initialize()
            print("Server info:", init_result.serverInfo)
            print("Server capabilities:", init_result.capabilities)

            tools = await session.list_tools()
            print("\nTools:")
            for tool in tools.tools:
                print(f"  {tool.name}: {tool.description}")


if __name__ == "__main__":
    asyncio.run(main())
