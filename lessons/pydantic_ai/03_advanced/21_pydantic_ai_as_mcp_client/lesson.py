"""
Lesson 21: Pydantic AI as an MCP client.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/03_advanced/21_pydantic_ai_as_mcp_client/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root. This lesson
launches server.py (in this same folder) as a subprocess over stdio.
"""

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset, StdioTransport

load_dotenv()

SERVER_SCRIPT = Path(__file__).parent / "server.py"

transport = StdioTransport(command=sys.executable, args=[str(SERVER_SCRIPT)])
toolset = MCPToolset(transport)

agent = Agent("google:gemini-3.5-flash-lite", toolsets=[toolset])


async def main() -> None:
    async with agent:
        result = await agent.run("What is 12 plus 30? Use a tool to compute it.")
        print("Output:", result.output)

        result = await agent.run("What is 6 times 7? Use a tool to compute it.")
        print("Output:", result.output)


if __name__ == "__main__":
    asyncio.run(main())
