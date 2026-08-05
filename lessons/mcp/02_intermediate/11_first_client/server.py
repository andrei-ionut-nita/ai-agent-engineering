"""
The server half of Lesson 11: a small, deliberately unremarkable
server, so lesson.py can focus entirely on the client side of the
connection.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("greeting-server")


@mcp.tool()
def greet(name: str) -> str:
    """Return a friendly greeting for the given name."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run(transport="stdio")
