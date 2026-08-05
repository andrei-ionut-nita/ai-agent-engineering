"""
Lesson 2: your first MCP server, called directly, no protocol yet.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/01_beginner/02_first_server/lesson.py

Running this file directly calls the tool function like any other
Python function, to see what @mcp.tool() actually did. To run this as
a real MCP server that a client could connect to, you would instead
run: mcp.run(transport="stdio") and leave it running, which is exactly
what Lesson 11's client will do.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("calculator-server")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


def main() -> None:
    # Calling the underlying function directly, no protocol involved,
    # same as calling calculator.invoke(...) in the langchain course.
    result = add(3, 4)
    print("Direct call result:", result)

    # @mcp.tool() registered this function on the server. FastMCP
    # doesn't expose the raw list quite as simply as a LangChain tool's
    # .name/.description, that's what tools/list is for, and what
    # Lesson 11's client will show you. For now: run this file with
    # `mcp.run(transport="stdio")` uncommented below, and it becomes a
    # real server a client can connect to.
    print("\nTo run this as a live server instead of a plain function:")
    print('  mcp.run(transport="stdio")')


if __name__ == "__main__":
    main()
