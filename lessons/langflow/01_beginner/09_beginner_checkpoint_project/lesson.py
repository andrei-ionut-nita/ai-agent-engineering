"""
Lesson 9: Checkpoint. A small Q&A flow, built end to end, everything
from Lessons 1-8 in one flow.

Read README.md in this folder first, then read this file top to bottom,
then run it with (Langflow must still be running from Lesson 1, and
LANGFLOW_API_KEY must be set, see Lesson 7's README):

    uv run python lessons/langflow/01_beginner/09_beginner_checkpoint_project/lesson.py
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
SESSION_ID = "checkpoint-demo"


def build_flow(session_id: str = SESSION_ID) -> Graph:
    chat_input = ChatInput()
    chat_input.set(session_id=session_id)

    memory = MemoryComponent()
    memory.set(session_id=session_id)

    # A system-style instruction baked into the template itself, plus
    # the two variables from Lesson 8: {history} and {user_input}.
    prompt = PromptComponent()
    prompt.set(
        template=(
            "You are a concise, helpful Q&A assistant. Answer in at most two sentences.\n\n"
            "Conversation so far:\n{history}\n\nUser: {user_input}\n\nAnswer:"
        ),
        history=memory.retrieve_messages_as_text,
        user_input=chat_input.message_response,
    )

    # API key from a Global Variable, Lesson 7's pattern.
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

    questions = [
        "What's the tallest mountain in the world?",
        "How tall is it, in meters?",
    ]
    for question in questions:
        answer = run_flow(flow_id, question, SESSION_ID)
        print(f"> {question}")
        print(f"{answer}\n")


if __name__ == "__main__":
    main()
