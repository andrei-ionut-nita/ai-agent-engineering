"""
Lesson 4: the Prompt component, {variables}, and wiring one component's
output into another component's variable.

Read README.md in this folder first, then read this file top to bottom,
then run it with (Langflow must still be running from Lesson 1):

    uv run python lessons/langflow/01_beginner/04_prompt_templates/lesson.py
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from lfx.components.google.google_generative_ai import GoogleGenerativeAIComponent
from lfx.components.input_output import ChatInput, ChatOutput
from lfx.components.models_and_agents import PromptComponent
from lfx.graph import Graph

from langflow.load import run_flow_from_json

load_dotenv()

FLOW_PATH = Path(__file__).parent / "flow.json"


def build_flow() -> Graph:
    chat_input = ChatInput()

    # PromptComponent's `template` field holds a string with {variable}
    # placeholders. Every {name} in the template becomes its own input
    # field on the component, here that's `user_input`, wired in from
    # Chat Input exactly like any other connection.
    prompt = PromptComponent()
    prompt.set(
        template="Answer as if you were a pirate.\n\nUser: {user_input}\n\nAnswer:",
        user_input=chat_input.message_response,
    )

    gemini = GoogleGenerativeAIComponent()
    gemini.set(
        input_value=prompt.build_prompt,
        model_name="gemini-3.5-flash-lite",
        api_key=os.environ["GOOGLE_API_KEY"],
    )

    chat_output = ChatOutput()
    chat_output.set(input_value=gemini.text_response)

    return Graph(start=chat_input, end=chat_output)


def main() -> None:
    graph = build_flow()
    rebuilt = graph.dump()
    assert len(rebuilt["data"]["nodes"]) == 4
    assert len(rebuilt["data"]["edges"]) == 3

    # flow.json is regenerated here, with your own GOOGLE_API_KEY baked
    # in, every time this script runs, see Lesson 2 for why.
    FLOW_PATH.write_text(json.dumps(rebuilt, indent=2))

    result = run_flow_from_json(flow=str(FLOW_PATH), input_value="What's the weather like?")
    message = result[0].outputs[0].messages[0].message
    print(f"Gemini said: {message}")


if __name__ == "__main__":
    main()
