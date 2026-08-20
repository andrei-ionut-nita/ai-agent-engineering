"""
Lesson 10: run_flow_from_json in depth. tweaks, the headless loader's way
of changing a flow's behavior without touching its flow.json.

Read README.md in this folder first, then read this file top to bottom,
then run it with (Langflow must still be running from Lesson 1):

    uv run python lessons/langflow/02_intermediate/10_run_flow_from_json_in_depth/lesson.py
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

# The exact component id assigned when flow.json was generated, see "Do
# this yourself" step 3 for how to find your own copy's id if you rebuild it.
GEMINI_COMPONENT_ID = "GoogleGenerativeAIComponent-lesson10"


def build_flow() -> Graph:
    chat_input = ChatInput()
    gemini = GoogleGenerativeAIComponent()
    gemini._id = GEMINI_COMPONENT_ID
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
    # in, every time this script runs, see Lesson 2 for why. Unrelated
    # to tweaks below, which really does leave the file alone.
    FLOW_PATH.write_text(json.dumps(rebuilt, indent=2))

    question = "What's a good name for a pet goldfish?"

    # No tweaks: whatever flow.json says.
    default = run_flow_from_json(flow=str(FLOW_PATH), input_value=question)
    print("Default system message:")
    print(default[0].outputs[0].messages[0].message, "\n")

    # tweaks overrides one field on one component, by component id, for
    # this run only. flow.json on disk is untouched.
    pirate = run_flow_from_json(
        flow=str(FLOW_PATH),
        input_value=question,
        tweaks={GEMINI_COMPONENT_ID: {"system_message": "Answer only in pirate speak."}},
    )
    print("Tweaked system message (pirate):")
    print(pirate[0].outputs[0].messages[0].message)


if __name__ == "__main__":
    main()
