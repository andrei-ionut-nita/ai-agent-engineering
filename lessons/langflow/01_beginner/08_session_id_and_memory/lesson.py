"""
Lesson 8: session_id and the Memory component, fixing the "it doesn't
remember anything" problem from Lesson 6.

Read README.md in this folder first, then read this file top to bottom,
then run it with (Langflow must still be running from Lesson 1, and
LANGFLOW_API_KEY must be set, see Lesson 7's README):

    uv run python lessons/langflow/01_beginner/08_session_id_and_memory/lesson.py

This lesson calls Langflow's REST API instead of run_flow_from_json.
Message history lives in the server's own database, run_flow_from_json
is a self-contained, isolated call with no shared state between
separate invocations, so two calls to it never see each other's
history, only real calls against the running server do. Lesson 11
covers the REST API properly, this is a preview of just enough of it to
keep this lesson honest.
"""

import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from lfx.components.google.google_generative_ai import GoogleGenerativeAIComponent
from lfx.components.input_output import ChatInput, ChatOutput
from lfx.components.models_and_agents import MemoryComponent, PromptComponent
from lfx.graph import Graph

load_dotenv()

LANGFLOW_URL = "http://127.0.0.1:7860"
HEADERS = {"x-api-key": os.environ["LANGFLOW_API_KEY"]}
FLOW_PATH = Path(__file__).parent / "flow.json"
SESSION_ID = "lesson-8-demo"


def build_flow(session_id: str = SESSION_ID) -> Graph:
    # Chat Input and Chat Output both take a session_id, every message
    # they handle gets stored under that ID automatically.
    chat_input = ChatInput()
    chat_input.set(session_id=session_id)

    # Message History (MemoryComponent) reads everything stored under a
    # session_id back out as one block of text.
    memory = MemoryComponent()
    memory.set(session_id=session_id)

    prompt = PromptComponent()
    prompt.set(
        template="Conversation so far:\n{history}\n\nUser: {user_input}\n\nAnswer:",
        history=memory.retrieve_messages_as_text,
        user_input=chat_input.message_response,
    )

    gemini = GoogleGenerativeAIComponent()
    gemini.set(input_value=prompt.build_prompt, model_name="gemini-3.5-flash-lite", api_key="GOOGLE_API_KEY")
    gemini._inputs["api_key"].load_from_db = True

    chat_output = ChatOutput()
    chat_output.set(input_value=gemini.text_response, session_id=session_id)

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


def run_flow(flow_id: str, input_value: str, session_id: str) -> str:
    response = httpx.post(
        f"{LANGFLOW_URL}/api/v1/run/{flow_id}",
        headers=HEADERS,
        json={"input_value": input_value, "session_id": session_id},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data["outputs"][0]["outputs"][0]["messages"][0]["message"]


def main() -> None:
    graph = build_flow()
    rebuilt = graph.dump()
    assert len(rebuilt["data"]["nodes"]) == 5

    flow_id = upload_flow()

    first = run_flow(flow_id, "My favorite color is teal.", SESSION_ID)
    print("Gemini:", first)

    second = run_flow(flow_id, "What is my favorite color?", SESSION_ID)
    print("Gemini:", second)


if __name__ == "__main__":
    main()
