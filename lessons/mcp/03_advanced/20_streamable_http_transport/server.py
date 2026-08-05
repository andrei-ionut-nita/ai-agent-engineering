"""The server half of Lesson 20, run over Streamable HTTP instead of stdio."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("http-demo-server", stateless_http=True, port=8931)


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
