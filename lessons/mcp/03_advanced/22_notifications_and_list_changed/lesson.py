"""
Lesson 22: reacting to a tools/list_changed notification.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/03_advanced/22_notifications_and_list_changed/lesson.py
"""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = Path(__file__).parent / "server.py"

notifications_seen: list = []


async def message_handler(message) -> None:
    notifications_seen.append(message)


async def main() -> None:
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER_SCRIPT)])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write, message_handler=message_handler) as session:
            await session.initialize()

            before = await session.list_tools()
            print("Before:", [tool.name for tool in before.tools])

            await session.call_tool("unlock_secret_tool", {})
            # Give the notification a moment to arrive on the stream.
            await asyncio.sleep(0.5)

            print(f"\nNotifications received: {len(notifications_seen)}")
            for notification in notifications_seen:
                print(" ", notification)

            # The well-behaved reaction: refresh, don't trust the old list.
            after = await session.list_tools()
            print("\nAfter refreshing:", [tool.name for tool in after.tools])


if __name__ == "__main__":
    asyncio.run(main())
