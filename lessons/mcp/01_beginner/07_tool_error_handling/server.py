"""
The server half of Lesson 7. lesson.py launches this as a subprocess
and talks to it over stdio, exactly like a real MCP host would.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("error-demo-server")


@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


if __name__ == "__main__":
    mcp.run(transport="stdio")
