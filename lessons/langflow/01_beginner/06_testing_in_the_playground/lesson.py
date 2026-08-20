"""
Lesson 6: the Playground, and what it's actually doing underneath.

Read README.md in this folder first, then read this file top to bottom,
then run it with (Langflow must still be running from Lesson 1):

    uv run python lessons/langflow/01_beginner/06_testing_in_the_playground/lesson.py
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from lfx.components.google.google_generative_ai import GoogleGenerativeAIComponent
from lfx.components.input_output import ChatInput, ChatOutput
from lfx.graph import Graph

from langflow.load import run_flow_from_json

load_dotenv()

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


def main() -> None:
    graph = build_flow()
    rebuilt = graph.dump()
    assert len(rebuilt["data"]["nodes"]) == 3

    # flow.json is regenerated here, with your own GOOGLE_API_KEY baked
    # in, every time this script runs, see Lesson 2 for why.
    FLOW_PATH.write_text(json.dumps(rebuilt, indent=2))

    # This loop is exactly what clicking Playground and typing three
    # separate messages does: the same flow, run fresh each time, one
    # call to run_flow_from_json (or the server's /run endpoint) per
    # message. No state carries over between these three calls, that's
    # Lesson 8's subject.
    questions = [
        "What's your name?",
        "What's the capital of France?",
        "Do you remember what I just asked you?",
    ]
    for question in questions:
        result = run_flow_from_json(flow=str(FLOW_PATH), input_value=question)
        answer = result[0].outputs[0].messages[0].message
        print(f"> {question}")
        print(f"{answer}\n")


if __name__ == "__main__":
    main()
