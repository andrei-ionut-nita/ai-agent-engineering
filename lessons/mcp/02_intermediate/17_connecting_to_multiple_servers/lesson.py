"""
Lesson 17: connecting one client to two different MCP servers.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/02_intermediate/17_connecting_to_multiple_servers/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root.
"""

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

HERE = Path(__file__).parent


async def main() -> None:
    client = MultiServerMCPClient(
        {
            "calculator": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(HERE / "calculator_server.py")],
            },
            "weather": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(HERE / "weather_server.py")],
            },
        }
    )

    # One call, both servers launched and listed.
    tools = await client.get_tools()
    print("Tools from both servers:", [tool.name for tool in tools])
    tools_by_name = {tool.name: tool for tool in tools}

    model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite").bind_tools(tools)
    messages = [HumanMessage("What's 12 plus 30, and what's the weather in Seattle?")]
    response = model.invoke(messages)
    messages.append(response)

    print("\nModel decided to call:")
    for call in response.tool_calls:
        print(f"  {call['name']}({call['args']})")
        result = await tools_by_name[call["name"]].ainvoke(call["args"])
        messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))

    final = model.invoke(messages)
    print("\nFinal answer:", final.content)


if __name__ == "__main__":
    asyncio.run(main())
