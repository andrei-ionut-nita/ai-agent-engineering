"""
Lesson 13: the same kind of Custom Component from Lesson 12, but built
to be called by an Agent as a tool, not wired directly into the main
chain. Also run directly via graph.arun(), same reason as Lesson 12,
see its README.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langflow/02_intermediate/13_custom_component_as_tool/lesson.py

No running Langflow server is required for this one.
"""

import asyncio
import os

from dotenv import load_dotenv
from lfx.custom.custom_component.component import Component
from lfx.components.google.google_generative_ai import GoogleGenerativeAIComponent
from lfx.components.input_output import ChatInput, ChatOutput
from lfx.components.models_and_agents.agent import AgentComponent
from lfx.field_typing import Tool
from lfx.graph import Graph
from lfx.io import MessageTextInput, Output

load_dotenv()


class WordLengthTool(Component):
    """A tool-shaped Custom Component. Instead of an output that feeds
    the next component directly (Lesson 12's pattern), its output
    method returns a LangChain Tool object, something an Agent can
    decide to call, or not, based on what it's asked.
    """

    display_name = "Word Length"
    description = "Counts the number of characters in a single word."
    name = "WordLengthTool"

    inputs = [
        MessageTextInput(name="word", display_name="Word"),
    ]
    outputs = [
        Output(display_name="Tool", name="tool", method="build_tool"),
    ]

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
    gemini.set(model_name="gemini-3.5-flash-lite", api_key=os.environ["GOOGLE_API_KEY"])

    word_length = WordLengthTool()

    agent = AgentComponent()
    agent.set(
        model=gemini.build_model,
        input_value=chat_input.message_response,
        tools=[word_length.build_tool],
        system_prompt="You are a helpful assistant. Use the word_length tool whenever asked about a word's length.",
    )

    chat_output = ChatOutput()
    chat_output.set(input_value=agent.message_response)
    return Graph(start=chat_input, end=chat_output)


def main() -> None:
    graph = build_flow()
    dumped = graph.dump()
    print(f"nodes: {len(dumped['data']['nodes'])}")

    graph.prepare()
    results = asyncio.run(
        graph.arun(inputs=[{"input_value": "How many letters are in the word 'xylophone'?"}])
    )
    message = results[0].outputs[0].messages[0].message
    print(f"Agent said: {message}")


if __name__ == "__main__":
    main()
