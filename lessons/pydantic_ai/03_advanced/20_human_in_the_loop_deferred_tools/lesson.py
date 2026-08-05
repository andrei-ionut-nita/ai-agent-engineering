"""
Lesson 20: human-in-the-loop with deferred tools.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/03_advanced/20_human_in_the_loop_deferred_tools/lesson.py

Uses TestModel, not a live Gemini call: the point of this lesson is the
approve/resume mechanics, not what a real model decides to do. No
GOOGLE_API_KEY needed.
"""

from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel
from pydantic_ai.tools import DeferredToolRequests, DeferredToolResults

agent = Agent("test", output_type=[str, DeferredToolRequests])


@agent.tool_plain(requires_approval=True)
def delete_file(path: str) -> str:
    """Delete a file at the given path.

    Args:
        path: The path of the file to delete.
    """
    return f"deleted {path}"


def main() -> None:
    test_model = TestModel(call_tools=["delete_file"])

    result = agent.run_sync("Please delete /tmp/foo.txt", model=test_model)
    print("First run output type:", type(result.output).__name__)

    if not isinstance(result.output, DeferredToolRequests):
        print("No approval needed, final answer:", result.output)
        return

    print("Pending approvals:")
    for call in result.output.approvals:
        print(f"  {call.tool_name}({call.args})")

    # A human (or a policy function) decides here. We approve every call.
    decisions = DeferredToolResults()
    for call in result.output.approvals:
        decisions.approvals[call.tool_call_id] = True

    final = agent.run_sync(
        message_history=result.all_messages(),
        deferred_tool_results=decisions,
        model=test_model,
    )
    print("\nAfter approval, final output:", final.output)


if __name__ == "__main__":
    main()
