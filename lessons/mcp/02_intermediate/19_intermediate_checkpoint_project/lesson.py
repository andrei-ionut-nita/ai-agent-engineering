"""
Lesson 19 (Checkpoint): an interactive Gemini chatbot backed by two
MCP servers.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/02_intermediate/19_intermediate_checkpoint_project/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root. Type your
questions, 'quit' to exit.
"""

import asyncio
import sys
from contextlib import AsyncExitStack
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

load_dotenv()

HERE = Path(__file__).parent


async def process_query(model, tools_by_name: dict, messages: list, query: str) -> str:
    messages.append(HumanMessage(query))
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


async def chat_loop(model, tools_by_name: dict) -> None:
    print("MCP Chatbot Started! Type your queries or 'quit' to exit.")
    messages: list = []
    while True:
        try:
            query = (await asyncio.to_thread(input, "\nQuery: ")).strip()
        except EOFError:
            break
        if query.lower() == "quit":
            break
        if not query:
            continue
        try:
            answer = await process_query(model, tools_by_name, messages, query)
            print(answer)
        except Exception as error:  # noqa: BLE001 -- surfaced to the user, loop keeps going
            print(f"Error: {error}")


async def main() -> None:
    client = MultiServerMCPClient(
        {
            "notes": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(HERE / "notes_server.py")],
            },
            "calculator": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(HERE / "calculator_server.py")],
            },
        }
    )
    # The notes server keeps its notes in lifespan-managed state
    # (Lesson 18), so it needs one session held open for the whole
    # conversation, client.get_tools() (Lessons 15-17) would open a
    # fresh session per call and reset that state every time. AsyncExitStack
    # keeps both servers' sessions open for main()'s whole lifetime.
    async with AsyncExitStack() as stack:
        notes_session = await stack.enter_async_context(client.session("notes"))
        calculator_session = await stack.enter_async_context(client.session("calculator"))

        tools = [
            *(await load_mcp_tools(notes_session)),
            *(await load_mcp_tools(calculator_session)),
        ]
        tools_by_name = {tool.name: tool for tool in tools}
        print("Connected with tools:", list(tools_by_name))

        model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite").bind_tools(tools)
        await chat_loop(model, tools_by_name)


if __name__ == "__main__":
    asyncio.run(main())
