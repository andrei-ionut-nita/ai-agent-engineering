"""
Lesson 26 (Capstone): a Gemini agent using the full Task Manager server.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/03_advanced/26_advanced_capstone_project/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root. Connects
to server.py over stdio, the same server that also runs over
Streamable HTTP (see README.md), and runs a short scripted multi-turn
conversation through Gemini.
"""

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

load_dotenv()

SERVER_SCRIPT = Path(__file__).parent / "server.py"


async def ask(model, tools_by_name: dict, messages: list, question: str) -> str:
    messages.append(HumanMessage(question))
    response = model.invoke(messages)
    messages.append(response)

    for call in response.tool_calls:
        tool = tools_by_name[call["name"]]
        result = await tool.ainvoke(call["args"])
        messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))

    if response.tool_calls:
        response = model.invoke(messages)
        messages.append(response)

    return str(response.content)


async def main() -> None:
    client = MultiServerMCPClient(
        {
            "tasks": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(SERVER_SCRIPT)],
            }
        }
    )

    # client.get_tools() (Lessons 15-17) opens a fresh session per tool
    # call, fine for a stateless calculator, but wrong here: the Task
    # Manager's lifespan state (Lesson 18) would reset every call, so
    # a second add_task would get id=1 again instead of id=2. Holding
    # one session open for the whole conversation, via client.session()
    # + load_mcp_tools(session), keeps the server's state intact across
    # every tool call in this script.
    async with client.session("tasks") as session:
        tools = await load_mcp_tools(session)
        tools_by_name = {tool.name: tool for tool in tools}
        print("Connected with tools:", list(tools_by_name))

        model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite").bind_tools(tools)
        messages: list = []

        for question in [
            "Add a task to write the MCP course.",
            "Add a task to review the pull request.",
            "Mark the first task as complete.",
            "Summarize where things stand across all my tasks.",
        ]:
            answer = await ask(model, tools_by_name, messages, question)
            print(f"\nQ: {question}")
            print(f"A: {answer}")


if __name__ == "__main__":
    asyncio.run(main())
