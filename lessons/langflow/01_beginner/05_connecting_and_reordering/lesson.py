"""
Lesson 5: edges determine execution order, not the order you wrote the
code in, and not where a box sits on the canvas.

Read README.md in this folder first, then read this file top to bottom,
then run it with (no Langflow server needed, this is all in-process
graph building):

    uv run python lessons/langflow/01_beginner/05_connecting_and_reordering/lesson.py
"""

from lfx.components.input_output import ChatInput, ChatOutput
from lfx.components.models_and_agents import PromptComponent
from lfx.graph import Graph


def main() -> None:
    # Instantiated out of order on purpose: Chat Output first, then
    # Chat Input, then Prompt in between. If order-of-definition mattered,
    # this would build a different flow than Lesson 4's. It doesn't.
    chat_output = ChatOutput()
    chat_input = ChatInput()
    prompt = PromptComponent()
    prompt.set(template="{user_input}", user_input=chat_input.message_response)
    chat_output.set(input_value=prompt.build_prompt)

    graph = Graph(start=chat_input, end=chat_output)
    graph.prepare()

    order = [vertex.display_name for vertex in graph.topological_sort()]
    print("Execution order (by edges, not by definition order):")
    for step, name in enumerate(order, start=1):
        print(f"  {step}. {name}")


if __name__ == "__main__":
    main()
