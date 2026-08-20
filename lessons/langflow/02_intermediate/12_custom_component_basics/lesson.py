"""
Lesson 12: Custom Components, plain Python classes that become canvas
boxes. Built and run entirely in-process, no server round trip, that's
deliberate, see README.md's "Why this lesson runs the graph directly"
section before reading further.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langflow/02_intermediate/12_custom_component_basics/lesson.py

No running Langflow server is required for this one.
"""

import asyncio

from lfx.custom.custom_component.component import Component
from lfx.components.input_output import ChatInput, ChatOutput
from lfx.graph import Graph
from lfx.io import MessageTextInput, Output
from lfx.schema.message import Message


class TitleCaseComponent(Component):
    """A Custom Component: a plain Python class, an inputs list, an
    outputs list, and a method per output. This is the entire contract,
    the same one every built-in component (ChatInput, Google Generative
    AI, the lot) is written to.
    """

    display_name = "Title Case"
    description = "Converts the input text to Title Case."
    name = "TitleCaseComponent"

    inputs = [
        MessageTextInput(name="input_value", display_name="Input"),
    ]
    outputs = [
        Output(display_name="Title Cased", name="output_value", method="to_title_case"),
    ]

    def to_title_case(self) -> Message:
        return Message(text=self.input_value.title())


def build_flow() -> Graph:
    chat_input = ChatInput()
    title_case = TitleCaseComponent()
    title_case.set(input_value=chat_input.message_response)
    chat_output = ChatOutput()
    chat_output.set(input_value=title_case.to_title_case)
    return Graph(start=chat_input, end=chat_output)


def main() -> None:
    graph = build_flow()
    dumped = graph.dump()
    assert len(dumped["data"]["nodes"]) == 3

    graph.prepare()
    results = asyncio.run(graph.arun(inputs=[{"input_value": "the trade-off between prototyping and production"}]))
    message = results[0].outputs[0].messages[0].message
    print(f"Title Cased: {message}")


if __name__ == "__main__":
    main()
