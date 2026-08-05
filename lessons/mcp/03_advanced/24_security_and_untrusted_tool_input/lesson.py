"""
Lesson 24: a real path traversal exploit, and the fix.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/03_advanced/24_security_and_untrusted_tool_input/lesson.py

data/shopping.txt is the file both tools are meant to read.
../secret.txt (one directory above data/) is what the vulnerable tool
should never be able to reach, but can.
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

            print("Legitimate call, both tools:")
            for tool_name in ("read_note_unsafe", "read_note_safe"):
                result = await session.call_tool(tool_name, {"filename": "shopping.txt"})
                print(f"  {tool_name}: {result.content[0].text.strip()}")

            print("\nAttack: filename='../secret.txt'")
            unsafe_attack = await session.call_tool("read_note_unsafe", {"filename": "../secret.txt"})
            print("  read_note_unsafe isError:", unsafe_attack.isError)
            print("  read_note_unsafe leaked:", unsafe_attack.content[0].text.strip())

            safe_attack = await session.call_tool("read_note_safe", {"filename": "../secret.txt"})
            print("  read_note_safe isError:", safe_attack.isError)
            print("  read_note_safe blocked it:", safe_attack.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
