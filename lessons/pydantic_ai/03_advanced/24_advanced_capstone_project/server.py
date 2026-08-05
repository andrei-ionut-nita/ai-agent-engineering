"""A tiny MCP server for the capstone, same shape as Lesson 21's."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("calculator-server")


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b


if __name__ == "__main__":
    mcp.run(transport="stdio")
