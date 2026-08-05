"""
The server this lesson inspects. Unlike earlier lessons, this file is
meant to be run directly and left running, connected to by the MCP
Inspector rather than by a lesson.py client.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("inspectable-server")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


@mcp.resource("notes://today")
def today_note() -> str:
    """Today's note."""
    return "Buy milk."


@mcp.prompt()
def greet(name: str) -> str:
    """Greet someone warmly."""
    return f"Please greet {name} warmly."


if __name__ == "__main__":
    mcp.run(transport="stdio")
