"""
Lesson 2: the smallest real flow, Chat Input -> Google Generative AI -> Chat Output.

Read README.md in this folder first (it has the GUI steps to do before
this file makes full sense), then read this file top to bottom, then
run it with (Langflow must still be running from Lesson 1):

    uv run python lessons/langflow/01_beginner/02_first_flow/lesson.py
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
    # Wires the same two connections you dragged by hand in the
    # browser. This is the code that produced flow.json in this folder,
    # Graph.dump() is the same JSON the canvas's own Export writes.
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
    assert len(rebuilt["data"]["edges"]) == 2

    # flow.json is regenerated here, with your own GOOGLE_API_KEY baked
    # in, every time this script runs. The copy checked into git ships
    # with that field blank on purpose, a flow.json is JSON, not a
    # secret, and shouldn't carry a live API key into version control.
    FLOW_PATH.write_text(json.dumps(rebuilt, indent=2))

    # The actual run: load flow.json from disk and run it once. No
    # browser involved, this is the headless path every later lesson
    # in this course builds on.
    result = run_flow_from_json(flow=str(FLOW_PATH), input_value="Say hello in exactly three words.")
    message = result[0].outputs[0].messages[0].message
    print(f"Gemini said: {message}")


if __name__ == "__main__":
    main()
