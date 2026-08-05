"""
Lesson 21: bearer token authentication on an HTTP MCP server.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/03_advanced/21_authenticating_http_servers/lesson.py
"""

import asyncio
import subprocess
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

SERVER_SCRIPT = Path(__file__).parent / "server.py"
SERVER_URL = "http://127.0.0.1:8932/mcp"


async def try_call(label: str, headers: dict[str, str] | None) -> None:
    print(f"{label}:")
    try:
        async with streamablehttp_client(SERVER_URL, headers=headers) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("add", {"a": 2, "b": 3})
                print("  succeeded:", result.content)
    except* Exception as group:  # noqa: BLE001 -- deliberately broad, this is a demo of failure modes
        for error in group.exceptions:
            print(f"  rejected: {type(error).__name__}: {error}")


async def wait_until_ready() -> None:
    for _ in range(20):
        try:
            async with streamablehttp_client(
                SERVER_URL, headers={"Authorization": f"Bearer secret-token-123"}
            ) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    return
        except Exception:
            await asyncio.sleep(0.25)
    raise RuntimeError("Server did not start in time.")


async def main() -> None:
    process = subprocess.Popen(
        [sys.executable, str(SERVER_SCRIPT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        await wait_until_ready()

        await try_call("No Authorization header", None)
        await try_call("Wrong token", {"Authorization": "Bearer wrong-token"})
        await try_call("Correct token", {"Authorization": "Bearer secret-token-123"})
    finally:
        process.terminate()
        process.wait()


if __name__ == "__main__":
    asyncio.run(main())
