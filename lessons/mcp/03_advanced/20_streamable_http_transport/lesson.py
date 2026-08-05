"""
Lesson 20: connecting to a server over Streamable HTTP instead of stdio.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/03_advanced/20_streamable_http_transport/lesson.py

This starts server.py as a background process (an HTTP server has its
own lifetime, unlike a stdio server a client launches and owns
directly), connects to it over HTTP, and shuts it down when done.
"""

import asyncio
import subprocess
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

SERVER_SCRIPT = Path(__file__).parent / "server.py"
SERVER_URL = "http://127.0.0.1:8931/mcp"


async def wait_until_ready(process: subprocess.Popen) -> None:
    # A real deployment would use a proper health check; for this
    # lesson, a short retry loop against the MCP endpoint itself is
    # enough to know the server is accepting connections.
    for _ in range(20):
        try:
            async with streamablehttp_client(SERVER_URL) as (read, write, _):
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
        await wait_until_ready(process)

        async with streamablehttp_client(SERVER_URL) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                print("Tools over HTTP:", [tool.name for tool in tools.tools])

                result = await session.call_tool("add", {"a": 4, "b": 5})
                print("add(4, 5) over HTTP ->", result.content)
    finally:
        process.terminate()
        process.wait()


if __name__ == "__main__":
    asyncio.run(main())
