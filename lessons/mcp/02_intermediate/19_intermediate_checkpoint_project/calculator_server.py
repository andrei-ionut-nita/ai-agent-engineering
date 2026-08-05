"""The second server for the intermediate checkpoint: a calculator."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("calculator-server")


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


if __name__ == "__main__":
    mcp.run(transport="stdio")
