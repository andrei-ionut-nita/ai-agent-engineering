"""The server half of Lesson 22: a tool that unlocks another tool."""

from mcp.server.fastmcp import Context, FastMCP

mcp = FastMCP("notify-demo-server")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


@mcp.tool()
async def unlock_secret_tool(ctx: Context) -> str:
    """Unlock a hidden bonus tool."""

    def multiply(a: int, b: int) -> int:
        return a * b

    multiply.__doc__ = "Multiply two numbers."
    mcp.add_tool(multiply, name="multiply")

    # Registering the tool doesn't announce it, this does.
    await ctx.session.send_tool_list_changed()
    return "Unlocked the multiply tool!"


if __name__ == "__main__":
    mcp.run(transport="stdio")
