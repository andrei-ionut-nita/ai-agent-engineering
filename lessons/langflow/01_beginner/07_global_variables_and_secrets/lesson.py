"""
Lesson 7: reading the Gemini API key from a Global Variable instead of
hardcoding it, and how a component field opts into that.

Read README.md in this folder first, then read this file top to bottom,
then run it with (Langflow must still be running from Lesson 1, and
LANGFLOW_API_KEY must be set, see README.md):

    uv run python lessons/langflow/01_beginner/07_global_variables_and_secrets/lesson.py

This lesson calls Langflow's REST API instead of run_flow_from_json.
Global Variable resolution (load_from_db fields) needs a real request
context to look up which user's variables to read, something the
headless run_flow_from_json loader doesn't have, it only resolves
correctly through an actual server request. Lesson 11 covers the REST
API properly, this is a preview of just enough of it to keep this
lesson honest.
"""

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
    gemini.set(input_value=chat_input.message_response, model_name="gemini-3.5-flash-lite", api_key="GOOGLE_API_KEY")
    # .set() resets load_from_db to False by default (it assumes you're
    # setting a literal value), since we want "GOOGLE_API_KEY" read as a
    # variable NAME rather than a literal key string, it has to be
    # turned back on explicitly, the same flag the canvas's own
    # Global-Variable dropdown sets when you pick a variable there.
    gemini._inputs["api_key"].load_from_db = True

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


def main() -> None:
    graph = build_flow()
    rebuilt = graph.dump()
    assert len(rebuilt["data"]["nodes"]) == 3

    flow_id = upload_flow()
    message = run_flow(flow_id, "Say hello in exactly three words.")
    print(f"Gemini said: {message}")


if __name__ == "__main__":
    main()
