"""
Lesson 14: the built-in Agent component, and the two tools it can turn
on with a checkbox, no custom code required.

Read README.md in this folder first, then read this file top to bottom,
then run it with (Langflow must still be running from Lesson 1):

    uv run python lessons/langflow/02_intermediate/14_agent_component/lesson.py
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from lfx.components.google.google_generative_ai import GoogleGenerativeAIComponent
from lfx.components.input_output import ChatInput, ChatOutput
from lfx.components.models_and_agents.agent import AgentComponent
from lfx.graph import Graph
from langflow.load import run_flow_from_json

load_dotenv()

FLOW_PATH = Path(__file__).parent / "flow.json"


def build_flow() -> Graph:
    chat_input = ChatInput()

    gemini = GoogleGenerativeAIComponent()
    gemini.set(model_name="gemini-3.5-flash-lite", api_key=os.environ["GOOGLE_API_KEY"])

    agent = AgentComponent()
    agent.set(
        model=gemini.build_model,
        input_value=chat_input.message_response,
        add_calculator_tool=True,
        add_current_date_tool=True,
        system_prompt="You are a helpful assistant with a calculator and a date tool.",
    )

    chat_output = ChatOutput()
    chat_output.set(input_value=agent.message_response)
    return Graph(start=chat_input, end=chat_output)


def main() -> None:
    graph = build_flow()
    rebuilt = graph.dump()
    print(f"nodes: {len(rebuilt['data']['nodes'])}")

    # flow.json is regenerated here, with your own GOOGLE_API_KEY baked
    # in, every time this script runs, see Lesson 2 for why.
    FLOW_PATH.write_text(json.dumps(rebuilt, indent=2))

    result = run_flow_from_json(flow=str(FLOW_PATH), input_value="What is 47 times 6, and what's today's date?")
    message = result[0].outputs[0].messages[0].message
    print(f"Agent said: {message}")


if __name__ == "__main__":
    main()
