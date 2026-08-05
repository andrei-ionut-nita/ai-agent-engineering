"""
Lesson 9: confirming from Python what the MCP Inspector showed you.

Read README.md in this folder first. Before running this file, try the
Inspector itself against server.py in this folder:

    npx @modelcontextprotocol/inspector \\
        uv run python lessons/mcp/01_beginner/09_inspecting_with_mcp_inspector/server.py

Then run this file:

    uv run python lessons/mcp/01_beginner/09_inspecting_with_mcp_inspector/lesson.py
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

            tools = await session.list_tools()
            print("Tools (same as the Inspector's tools/list):")
            for tool in tools.tools:
                print(f"  {tool.name}: {tool.description}")

            result = await session.call_tool("add", {"a": 2, "b": 3})
            print("\nadd(2, 3) ->", result.content)


if __name__ == "__main__":
    asyncio.run(main())
