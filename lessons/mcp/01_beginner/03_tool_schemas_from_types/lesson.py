"""
Lesson 3: how @mcp.tool() turns type hints into a JSON Schema.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/01_beginner/03_tool_schemas_from_types/lesson.py

No client yet: mcp.list_tools() lets the server tell us directly what
a client would eventually see over tools/list.
"""

import asyncio

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("schema-demo-server")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


@mcp.tool()
def add_with_default(a: int, b: int = 0) -> int:
    """Add two numbers, b defaults to 0 if omitted."""
    return a + b


async def show_schema(name: str) -> None:
    tools = await mcp.list_tools()
    tool = next(t for t in tools if t.name == name)
    print(f"\nTool: {tool.name}")
    print(f"  description: {tool.description}")
    print(f"  inputSchema: {tool.inputSchema}")


async def main() -> None:
    # Everything printed here came from the function's name, docstring,
    # and type hints, nothing else. This is the entire contract a
    # client has to work with.
    await show_schema("add")
    await show_schema("add_with_default")


if __name__ == "__main__":
    asyncio.run(main())
