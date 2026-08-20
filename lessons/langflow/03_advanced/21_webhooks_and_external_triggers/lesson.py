"""
Lesson 21: the Webhook component, a flow triggered by an external
system's HTTP POST, not by a person typing into the Playground.

Read README.md in this folder first, then read this file top to bottom,
then run it with (Langflow must still be running from Lesson 1):

    uv run python lessons/langflow/03_advanced/21_webhooks_and_external_triggers/lesson.py
"""

import os
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv
from lfx.components.input_output import ChatOutput
from lfx.components.input_output.webhook import WebhookComponent
from lfx.graph import Graph

load_dotenv()

LANGFLOW_URL = "http://127.0.0.1:7860"
HEADERS = {"x-api-key": os.environ["LANGFLOW_API_KEY"]}
FLOW_PATH = Path(__file__).parent / "flow.json"


def build_flow() -> Graph:
    webhook = WebhookComponent()
    chat_output = ChatOutput()
    chat_output.set(input_value=webhook.build_data)
    return Graph(start=webhook, end=chat_output)


def upload_flow() -> str:
    with FLOW_PATH.open("rb") as f:
        response = httpx.post(
            f"{LANGFLOW_URL}/api/v1/flows/upload/",
            headers=HEADERS,
            files={"file": ("flow.json", f, "application/json")},
        )
    response.raise_for_status()
    return response.json()[0]["id"]


def trigger_webhook(flow_id: str, payload: dict) -> None:
    # Notice: no /run here, /webhook. It answers immediately with 202
    # Accepted, the flow runs in the background, the caller doesn't
    # wait for it, same shape as a real payment provider or CI system
    # firing a webhook and moving on without waiting for your handler.
    response = httpx.post(f"{LANGFLOW_URL}/api/v1/webhook/{flow_id}", headers=HEADERS, json=payload, timeout=15)
    response.raise_for_status()
    print(f"Webhook accepted: {response.status_code} {response.json()}")


def wait_for_result(flow_id: str) -> str:
    # The webhook run gets its own auto-generated session_id (the
    # flow_id itself), not one you can set ahead of time, so this polls
    # for any message tied to this flow rather than a fixed session_id.
    for _ in range(15):
        time.sleep(1)
        response = httpx.get(
            f"{LANGFLOW_URL}/api/v1/monitor/messages",
            headers=HEADERS,
            params={"flow_id": flow_id},
        )
        response.raise_for_status()
        messages = response.json()
        if messages:
            return messages[-1]["text"]
    msg = "No message appeared within 15 seconds."
    raise TimeoutError(msg)


def delete_flow(flow_id: str) -> None:
    httpx.delete(f"{LANGFLOW_URL}/api/v1/flows/{flow_id}", headers=HEADERS).raise_for_status()


def main() -> None:
    graph = build_flow()
    dumped = graph.dump()
    print(f"nodes: {len(dumped['data']['nodes'])}")

    flow_id = upload_flow()
    trigger_webhook(flow_id, {"event": "order_placed", "order_id": 42})
    result = wait_for_result(flow_id)
    print(f"Flow's stored output:\n{result}")
    delete_flow(flow_id)


if __name__ == "__main__":
    main()
