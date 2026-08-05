"""
Lesson 25: validating a real mcpServers config before using it.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/03_advanced/25_connecting_to_claude_desktop_and_code/lesson.py

This builds the exact command/args pair you'd put in
claude_desktop_config.json or .mcp.json, then launches it the same way
a real host would, to confirm it's wired correctly before touching a
real host's config file.
"""

import asyncio
import json
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# lessons/mcp/03_advanced/25_.../lesson.py -> project root is 4 levels up.
PROJECT_ROOT = Path(__file__).resolve().parents[4]
SERVER_SCRIPT = "lessons/mcp/01_beginner/10_beginner_checkpoint_project/server.py"


def build_mcp_server_config() -> dict:
    """The exact config a real host's mcpServers entry would need."""
    return {
        "notes": {
            "command": "uv",
            "args": ["--directory", str(PROJECT_ROOT), "run", "python", SERVER_SCRIPT],
        }
    }


async def main() -> None:
    config = build_mcp_server_config()
    print("This is what would go in claude_desktop_config.json or .mcp.json:")
    print(json.dumps({"mcpServers": config}, indent=2))

    server_config = config["notes"]
    params = StdioServerParameters(command=server_config["command"], args=server_config["args"])

    print("\nLaunching it exactly the way a real host would...")
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            init_result = await session.initialize()
            print(f"Connected to: {init_result.serverInfo.name}")

            tools = await session.list_tools()
            print("Tools a host would see:", [tool.name for tool in tools.tools])
            print("\nConfig verified, safe to copy into a real host's config file.")


if __name__ == "__main__":
    asyncio.run(main())
