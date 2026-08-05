"""
Lesson 14: testing agents with TestModel.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/02_intermediate/14_testing_agents_with_testmodel/lesson.py

No GOOGLE_API_KEY needed: TestModel never makes a real network call.
"""

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel


class Answer(BaseModel):
    value: int


agent = Agent(
    "google:gemini-3.5-flash-lite", output_type=Answer, defer_model_check=True
)


@agent.tool_plain
def add(a: int, b: int) -> int:
    """Add two integers together."""
    return a + b


def main() -> None:
    print("Default TestModel: auto-calls every registered tool.")
    with agent.override(model=TestModel()):
        result = agent.run_sync("add 2 and 3")
    print("Output:", result.output)
    tool_calls = [
        part.tool_name
        for message in result.all_messages()
        for part in message.parts
        if part.part_kind == "tool-call"
    ]
    print("Tools the model called:", tool_calls)

    print("\nTestModel with a pinned output, still real validation:")
    with agent.override(model=TestModel(custom_output_args={"value": 42})):
        result = agent.run_sync("whatever")
    print("Output:", result.output)
    assert result.output.value == 42
    print("Assertion passed: output.value == 42")


if __name__ == "__main__":
    main()
