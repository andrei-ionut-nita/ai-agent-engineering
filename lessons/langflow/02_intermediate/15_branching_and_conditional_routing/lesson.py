"""
Lesson 15: the Conditional Router component, one input, two possible
paths, only one of which actually runs, Langflow's answer to
langgraph's conditional edges.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langflow/02_intermediate/15_branching_and_conditional_routing/lesson.py

No running Langflow server is required for this one.
"""

import asyncio

from lfx.components.flow_controls.conditional_router import ConditionalRouterComponent
from lfx.components.input_output import ChatInput, ChatOutput
from lfx.graph import Graph
from lfx.schema.message import Message


def build_flow(text: str) -> Graph:
    chat_input = ChatInput()
    chat_input.set(input_value=text)

    router = ConditionalRouterComponent()
    router.set(
        input_text=chat_input.message_response,
        operator="contains",
        match_text="urgent",
        case_sensitive=False,
        true_case_message=Message(text="Escalating to a human, priority queue."),
        false_case_message=Message(text="Logged, we'll get to it in the usual order."),
    )

    urgent_output = ChatOutput()
    urgent_output.set(input_value=router.true_response)

    normal_output = ChatOutput()
    normal_output.set(input_value=router.false_response)

    graph = Graph()
    graph.add_component(chat_input)
    graph.add_component(router)
    graph.add_component(urgent_output)
    graph.add_component(normal_output)
    return graph


def main() -> None:
    for text in ["This is urgent, my payment failed!", "Just checking in, no rush."]:
        graph = build_flow(text)
        graph.prepare()
        results = asyncio.run(graph.arun(inputs=[{}]))
        print(f"Input: {text}")
        for run_output in results:
            for out in run_output.outputs:
                print(f"  -> {out.component_display_name}: {out.messages[0].message}")
        print()


if __name__ == "__main__":
    main()
