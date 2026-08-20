"""
Lesson 11: the REST API on its own terms. Beginner borrowed a slice of
it early (Lessons 7-8) out of necessity, this lesson covers the rest of
its surface: listing flows, deleting them, and the auth header every
call needs.

Read README.md in this folder first, then read this file top to bottom,
then run it with (Langflow must still be running from Lesson 1, and
LANGFLOW_API_KEY must be set, see Lesson 7's README):

    uv run python lessons/langflow/02_intermediate/11_rest_api_and_auth/lesson.py
"""

import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from lfx.components.google.google_generative_ai import GoogleGenerativeAIComponent
from lfx.components.input_output import ChatInput, ChatOutput
from lfx.graph import Graph

load_dotenv()

LANGFLOW_URL = "http://127.0.0.1:7860"
HEADERS = {"x-api-key": os.environ["LANGFLOW_API_KEY"]}
FLOW_PATH = Path(__file__).parent / "flow.json"


def build_flow() -> Graph:
    chat_input = ChatInput()
    gemini = GoogleGenerativeAIComponent()
    gemini.set(
        input_value=chat_input.message_response,
        model_name="gemini-3.5-flash-lite",
        api_key=os.environ["GOOGLE_API_KEY"],
    )
    chat_output = ChatOutput()
    chat_output.set(input_value=gemini.text_response)
    return Graph(start=chat_input, end=chat_output)


def upload_flow() -> str:
    with FLOW_PATH.open("rb") as f:
        response = httpx.post(
            f"{LANGFLOW_URL}/api/v1/flows/upload/",
            headers=HEADERS,
            files={"file": ("flow.json", f, "application/json")},
        )
    response.raise_for_status()
    return response.json()[0]["id"]


def list_flows() -> list[dict]:
    response = httpx.get(f"{LANGFLOW_URL}/api/v1/flows/", headers=HEADERS)
    response.raise_for_status()
    return response.json()


def run_flow(flow_id: str, input_value: str) -> str:
    response = httpx.post(
        f"{LANGFLOW_URL}/api/v1/run/{flow_id}",
        headers=HEADERS,
        json={"input_value": input_value},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data["outputs"][0]["outputs"][0]["messages"][0]["message"]


def delete_flow(flow_id: str) -> None:
    response = httpx.delete(f"{LANGFLOW_URL}/api/v1/flows/{flow_id}", headers=HEADERS)
    response.raise_for_status()


def main() -> None:
    graph = build_flow()
    rebuilt = graph.dump(name="lesson-11-rest-api-and-auth")
    assert len(rebuilt["data"]["nodes"]) == 3

    # flow.json is regenerated here, with your own GOOGLE_API_KEY baked
    # in, every time this script runs, see Lesson 2 for why, upload_flow()
    # below uploads whatever's on disk.
    FLOW_PATH.write_text(json.dumps(rebuilt, indent=2))

    # No auth header at all: the server rejects it before it even looks
    # at the flow.
    unauthenticated = httpx.get(f"{LANGFLOW_URL}/api/v1/flows/")
    print(f"No x-api-key header: HTTP {unauthenticated.status_code}")

    flow_id = upload_flow()
    print(f"Uploaded, flow_id: {flow_id}")

    flows = list_flows()
    print(f"Flows on the server: {len(flows)}")

    answer = run_flow(flow_id, "Say hello in exactly three words.")
    print(f"Gemini said: {answer}")

    delete_flow(flow_id)
    flows_after = list_flows()
    print(f"Flows after delete: {len(flows_after)}")


if __name__ == "__main__":
    main()
