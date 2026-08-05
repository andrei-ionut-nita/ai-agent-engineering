"""The server half of Lesson 14: tools returning image and mixed content."""

from mcp.server.fastmcp import FastMCP, Image

mcp = FastMCP("content-demo-server")

# A minimal valid 1x1 red PNG, just so this lesson has real image bytes
# to send across the connection without needing an image file on disk.
_TINY_RED_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d494844520000000100000001080200000090"
    "7753de0000000c4944415478da6360606000000004000101fa50f10a0000"
    "000049454e44ae426082"
)


@mcp.tool()
def make_thumbnail() -> Image:
    """Return a small PNG thumbnail."""
    return Image(data=_TINY_RED_PNG, format="png")


@mcp.tool()
def make_thumbnail_with_caption() -> list:
    """Return a caption and a thumbnail together."""
    return ["Here is your thumbnail:", Image(data=_TINY_RED_PNG, format="png")]


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


if __name__ == "__main__":
    mcp.run(transport="stdio")
