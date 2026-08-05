"""
Lesson 12: multi-agent delegation.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/02_intermediate/12_multi_agent_delegation/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root.
"""

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

load_dotenv()

joke_agent = Agent(
    "google:gemini-3.5-flash-lite",
    system_prompt="You write one short joke about the given topic.",
)

main_agent = Agent(
    "google:gemini-3.5-flash-lite",
    system_prompt=(
        "You are a helpful assistant. Use the tell_joke tool whenever "
        "the user asks for a joke."
    ),
)


@main_agent.tool
def tell_joke(ctx: RunContext[None], topic: str) -> str:
    """Delegate to the joke-writing agent for a topic.

    Args:
        topic: What the joke should be about.
    """
    result = joke_agent.run_sync(topic, usage=ctx.usage)
    return result.output


def main() -> None:
    result = main_agent.run_sync("Tell me a joke about cats.")
    print("Output:", result.output)
    print("Combined usage (main + delegated):", result.usage)


if __name__ == "__main__":
    main()
