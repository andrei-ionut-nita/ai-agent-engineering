"""
Lesson 20: `lfx serve`, a standalone API server for one flow, no full
`langflow run` UI server involved at all. This is what "deploying a
flow" looks like once it's graduated past the Playground.

Read README.md in this folder first, then read this file top to bottom,
then run it with (LANGFLOW_API_KEY must be set, see Lesson 7's README):

    uv run python lessons/langflow/03_advanced/20_deploying_a_flow_as_a_service/lesson.py

This lesson starts its own lightweight server, no `langflow run` from
Lesson 1 needed for this one.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

PORT = 8123
SERVE_URL = f"http://127.0.0.1:{PORT}"
HEADERS = {"x-api-key": os.environ["LANGFLOW_API_KEY"]}
FLOW_PATH = Path(__file__).parent.parent.parent / "01_beginner" / "02_first_flow" / "flow.json"


def start_server() -> subprocess.Popen:
    process = subprocess.Popen(
        [sys.executable, "-m", "lfx", "serve", str(FLOW_PATH), "--port", str(PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env={**os.environ},
    )
    for _ in range(30):
        try:
            httpx.get(f"{SERVE_URL}/flows", headers=HEADERS, timeout=1)
            return process
        except httpx.TransportError:
            time.sleep(1)
    msg = "lfx serve did not come up in time"
    raise RuntimeError(msg)


def main() -> None:
    process = start_server()
    try:
        flows = httpx.get(f"{SERVE_URL}/flows", headers=HEADERS).json()
        flow_id = flows[0]["id"]
        print(f"Served flow: {flows[0]['title']} ({flow_id})")

        response = httpx.post(
            f"{SERVE_URL}/flows/{flow_id}/run",
            headers=HEADERS,
            json={"input_value": "Say hello in exactly three words."},
            timeout=30,
        )
        response.raise_for_status()
        print(f"Result: {response.json()['result']}")
    finally:
        process.terminate()
        process.wait(timeout=10)


if __name__ == "__main__":
    main()
