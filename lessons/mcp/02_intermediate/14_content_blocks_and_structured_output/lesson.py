"""
Lesson 14: content blocks, image content, and structured output.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/02_intermediate/14_content_blocks_and_structured_output/lesson.py
"""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = Path(__file__).parent / "server.py"


async def main() -> None:
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER_SCRIPT)])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            image_result = await session.call_tool("make_thumbnail", {})
            print("make_thumbnail content blocks:")
            for block in image_result.content:
                print(f"  {type(block).__name__}: mimeType={getattr(block, 'mimeType', None)}")

            mixed_result = await session.call_tool("make_thumbnail_with_caption", {})
            print("\nmake_thumbnail_with_caption content blocks (mixed):")
            for block in mixed_result.content:
                print(f"  {type(block).__name__}")

            typed_result = await session.call_tool("add", {"a": 2, "b": 3})
            print("\nadd's content (human-readable):", typed_result.content)
            print("add's structuredContent (typed):", typed_result.structuredContent)


if __name__ == "__main__":
    asyncio.run(main())
