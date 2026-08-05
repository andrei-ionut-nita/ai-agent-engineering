"""
Lesson 13: reading resources and getting prompts from a client.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/02_intermediate/13_reading_resources_and_prompts/lesson.py
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

            resources = await session.list_resources()
            print("Resources:")
            for resource in resources.resources:
                print(f"  {resource.uri}: {resource.description}")

            resource_content = await session.read_resource("notes://today")
            print("\nnotes://today contents:")
            for item in resource_content.contents:
                print(f"  ({item.mimeType}) {item.text}")

            prompts = await session.list_prompts()
            print("\nPrompts:")
            for prompt in prompts.prompts:
                print(f"  {prompt.name}: {prompt.description}")

            filled_in = await session.get_prompt(
                "code_review",
                {"language": "python", "code": "print('hello')"},
            )
            print("\ncode_review messages:")
            for message in filled_in.messages:
                print(f"  [{message.role}] {message.content.text}")


if __name__ == "__main__":
    asyncio.run(main())
