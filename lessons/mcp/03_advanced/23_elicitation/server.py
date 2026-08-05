"""The server half of Lesson 23: a tool that asks before acting."""

from pydantic import BaseModel, Field

from mcp.server.fastmcp import Context, FastMCP

mcp = FastMCP("elicit-demo-server")


class ConfirmDeletion(BaseModel):
    confirm: bool = Field(description="Type true to confirm deletion.")


@mcp.tool()
async def delete_file(filename: str, ctx: Context) -> str:
    """Delete a file, after asking the user to confirm."""
    result = await ctx.elicit(
        message=f"Really delete '{filename}'?",
        schema=ConfirmDeletion,
    )
    if result.action != "accept" or not result.data.confirm:
        return "Deletion cancelled."
    return f"Deleted '{filename}'."


if __name__ == "__main__":
    mcp.run(transport="stdio")
