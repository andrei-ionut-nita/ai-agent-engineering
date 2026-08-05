"""
Lesson 15: wiring MCP tools into a LangChain/Gemini model.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/02_intermediate/15_wiring_an_llm_to_mcp_tools/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root, same as
every langchain lesson.
"""

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

SERVER_SCRIPT = Path(__file__).parent / "server.py"


async def main() -> None:
    # MultiServerMCPClient manages the connection lifecycle: launching
    # the server, listing its tools, converting each one into a
    # LangChain BaseTool. "calculator" is just a label we chose.
    client = MultiServerMCPClient(
        {
            "calculator": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(SERVER_SCRIPT)],
            }
        }
    )
    tools = await client.get_tools()
    print("LangChain tools converted from MCP:", [tool.name for tool in tools])

    # From here on, this is exactly langchain/14_tool_calling: bind the
    # tools, invoke the model, read tool_calls off the response.
    model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite").bind_tools(tools)
    response = model.invoke("What is 12 plus 30? Use the tool to compute it.")

    print("\nModel's tool calls:")
    for call in response.tool_calls:
        print(f"  {call['name']}({call['args']})")


if __name__ == "__main__":
    asyncio.run(main())
