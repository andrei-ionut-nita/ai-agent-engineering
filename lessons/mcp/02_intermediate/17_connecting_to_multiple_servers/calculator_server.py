"""The first of Lesson 17's two servers: a calculator."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("calculator-server")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


if __name__ == "__main__":
    mcp.run(transport="stdio")
