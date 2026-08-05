"""
The broken half of Lesson 8: a stdio server that calls print() inside a
tool. Standard output is the JSON-RPC wire on this transport, so this
text lands on the same stream as protocol messages.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("bad-server")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    print("Processing request", flush=True)  # corrupts stdio!
    return a + b


if __name__ == "__main__":
    mcp.run(transport="stdio")
