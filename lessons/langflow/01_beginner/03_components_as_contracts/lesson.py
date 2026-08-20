"""
Lesson 3: components as typed contracts, and what happens when you
connect two ports that don't agree.

Read README.md in this folder first, then read this file top to bottom,
then run it with (no Langflow server needed for this one, it's all
in-process graph building):

    uv run python lessons/langflow/01_beginner/03_components_as_contracts/lesson.py
"""

import os

from dotenv import load_dotenv
from lfx.components.google.google_generative_ai import GoogleGenerativeAIComponent
from lfx.components.input_output import ChatInput, ChatOutput
from lfx.graph import Graph

load_dotenv()


def main() -> None:
    gemini = GoogleGenerativeAIComponent()
    for field in gemini.inputs:
        input_types = getattr(field, "input_types", None)
        if input_types:
            print(f"Google Generative AI input {field.name!r} only accepts: {input_types}")

    # A valid connection: ChatInput's message output (a Message) into
    # the model's input_value field, which declares input_types=['Message'].
    chat_input = ChatInput()
    gemini.set(
        input_value=chat_input.message_response,
        model_name="gemini-3.5-flash-lite",
        api_key=os.environ["GOOGLE_API_KEY"],
    )
    chat_output = ChatOutput()
    chat_output.set(input_value=gemini.text_response)
    Graph(start=chat_input, end=chat_output)
    print("Valid connection (Message -> Input): graph builds fine.")

    # An invalid connection: the same Message output, wired into
    # `temperature`, a field that declares no input_types at all (it's a
    # plain slider value, not a connectable port). Every field CAN be
    # set programmatically with .set(), the type contract is enforced
    # when the graph is assembled, not at .set() time.
    bad_input = ChatInput()
    bad_gemini = GoogleGenerativeAIComponent()
    bad_gemini.set(input_value=bad_input.message_response, api_key=os.environ["GOOGLE_API_KEY"])
    bad_gemini.set(temperature=bad_input.message_response)
    bad_output = ChatOutput()
    bad_output.set(input_value=bad_gemini.text_response)
    try:
        Graph(start=bad_input, end=bad_output)
    except ValueError as e:
        print(f"Invalid connection (Message -> Temperature) rejected: {e}")


if __name__ == "__main__":
    main()
