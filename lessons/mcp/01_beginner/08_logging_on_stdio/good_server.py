"""
The fixed half of Lesson 8: same server, but debug output goes through
logging (stderr) instead of print() (stdout).
"""

import logging

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)
mcp = FastMCP("good-server")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    logger.info("Processing request")  # writes to stderr, safe
    return a + b


if __name__ == "__main__":
    mcp.run(transport="stdio")
