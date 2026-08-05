"""
Lesson 4: multiple tools registered on one server.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/01_beginner/04_multiple_tools/lesson.py
"""

import asyncio

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("kitchen-server")


@mcp.tool()
def convert_celsius_to_fahrenheit(celsius: float) -> float:
    """Convert a Celsius temperature to Fahrenheit."""
    return celsius * 9 / 5 + 32


@mcp.tool()
def convert_cups_to_milliliters(cups: float) -> float:
    """Convert a volume in US cups to milliliters."""
    return cups * 236.588


async def main() -> None:
    # Calling both directly, no protocol involved, to confirm the math.
    print("100C in F:", convert_celsius_to_fahrenheit(100))
    print("2 cups in mL:", convert_cups_to_milliliters(2))

    # tools/list returns both, this is what a client (Lesson 11) or an
    # AI deciding which tool to use would actually see.
    tools = await mcp.list_tools()
    print("\nRegistered tools:")
    for tool in tools:
        print(f"  {tool.name}: {tool.description}")


if __name__ == "__main__":
    asyncio.run(main())
