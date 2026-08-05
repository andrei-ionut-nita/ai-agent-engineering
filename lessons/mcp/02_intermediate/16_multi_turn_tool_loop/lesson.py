"""
Lesson 16: the full ask/call/respond loop, across multiple turns.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/02_intermediate/16_multi_turn_tool_loop/lesson.py

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

SERVER_SCRIPT = Path(__file__).parent / "server.py"


async def ask(model, tools_by_name: dict, messages: list, question: str) -> str:
    messages.append(HumanMessage(question))
    response = model.invoke(messages)
    messages.append(response)

    # Run every tool the model asked for, and hand each result back as
    # a ToolMessage tagged with the matching tool_call_id.
    for call in response.tool_calls:
        tool = tools_by_name[call["name"]]
        result = await tool.ainvoke(call["args"])
        messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))

    if response.tool_calls:
        response = model.invoke(messages)
        messages.append(response)

    return response.content


async def main() -> None:
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
    tools_by_name = {tool.name: tool for tool in tools}

    model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite").bind_tools(tools)
    messages: list = []

    first_answer = await ask(model, tools_by_name, messages, "What is 12 plus 30?")
    print("Q1: What is 12 plus 30?")
    print("A1:", first_answer)

    # This second question only makes sense with the first turn's
    # answer still in `messages`, the same conversation-memory idea
    # as langchain/17_conversation_memory.
    second_answer = await ask(model, tools_by_name, messages, "Now add 8 to that result.")
    print("\nQ2: Now add 8 to that result.")
    print("A2:", second_answer)


if __name__ == "__main__":
    asyncio.run(main())
