"""The server half of Lesson 13: one resource, one prompt."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("notes-and-prompts-server")


@mcp.resource("notes://today")
def today_note() -> str:
    """Today's note."""
    return "Buy milk."


@mcp.prompt()
def code_review(language: str, code: str) -> str:
    """Ask for a structured code review of a snippet."""
    return (
        f"Please review this {language} code for bugs, style issues, "
        f"and possible improvements:\n\n{code}"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
