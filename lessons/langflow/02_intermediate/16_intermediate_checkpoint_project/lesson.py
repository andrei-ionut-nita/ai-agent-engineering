"""
Lesson 16: Checkpoint. Everything from Intermediate in one flow, an
Agent with a custom tool and a built-in tool, called over the REST API.

Read README.md in this folder first, then read this file top to bottom,
then run it with (Langflow must still be running from Lesson 1, and
LANGFLOW_API_KEY must be set, see Lesson 7's README):

    uv run python lessons/langflow/02_intermediate/16_intermediate_checkpoint_project/lesson.py
"""

import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from lfx.custom.custom_component.component import Component
from lfx.components.google.google_generative_ai import GoogleGenerativeAIComponent
from lfx.components.input_output import ChatInput, ChatOutput
from lfx.components.models_and_agents.agent import AgentComponent
from lfx.field_typing import Tool
from lfx.graph import Graph
from lfx.io import MessageTextInput, Output

load_dotenv()

LANGFLOW_URL = "http://127.0.0.1:7860"
HEADERS = {"x-api-key": os.environ["LANGFLOW_API_KEY"]}
FLOW_PATH = Path(__file__).parent / "flow.json"


class WordLengthTool(Component):
    """The same custom tool from Lesson 13, a Custom Component whose
    output is a Tool an Agent can call, not a fixed step in the chain.
    """

    display_name = "Word Length"
    description = "Counts the number of characters in a single word."
    name = "WordLengthTool"

    inputs = [MessageTextInput(name="word", display_name="Word")]
    outputs = [Output(display_name="Tool", name="tool", method="build_tool")]

    def build_tool(self) -> Tool:
        from langchain_core.tools import StructuredTool
        from pydantic import BaseModel, Field

        class WordLengthSchema(BaseModel):
            word: str = Field(..., description="The word to measure.")

        def _word_length(word: str) -> str:
            return str(len(word))

        return StructuredTool.from_function(
            name="word_length",
            description="Return the number of characters in a single word.",
            func=_word_length,
            args_schema=WordLengthSchema,
        )


def build_flow() -> Graph:
    chat_input = ChatInput()

    gemini = GoogleGenerativeAIComponent()
    gemini.set(model_name="gemini-3.5-flash-lite", api_key="GOOGLE_API_KEY")
    gemini._inputs["api_key"].load_from_db = True

    word_length = WordLengthTool()

    agent = AgentComponent()
    agent.set(
        model=gemini.build_model,
        input_value=chat_input.message_response,
        tools=[word_length.build_tool],
        add_calculator_tool=True,
        system_prompt=(
            "You are a helpful assistant. Use the word_length tool for questions about a "
            "word's length, and the calculator tool for arithmetic."
        ),
    )

    chat_output = ChatOutput()
    chat_output.set(input_value=agent.message_response)
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
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    return data["outputs"][0]["outputs"][0]["messages"][0]["message"]


def delete_flow(flow_id: str) -> None:
    httpx.delete(f"{LANGFLOW_URL}/api/v1/flows/{flow_id}", headers=HEADERS).raise_for_status()


def main() -> None:
    graph = build_flow()
    dumped = graph.dump()
    print(f"nodes: {len(dumped['data']['nodes'])}")

    flow_id = upload_flow()

    questions = [
        "How many letters are in the word 'checkpoint'?",
        "What is 12 times 12?",
    ]
    for question in questions:
        answer = run_flow(flow_id, question)
        print(f"> {question}")
        print(f"{answer}\n")

    delete_flow(flow_id)


if __name__ == "__main__":
    main()
