"""
Lesson 6: tools, the basics.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/01_beginner/06_tools_basics/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root.
"""

from dotenv import load_dotenv
from pydantic_ai import Agent

load_dotenv()

agent = Agent("google:gemini-3.5-flash-lite")


@agent.tool_plain
def add(a: int, b: int) -> int:
    """Add two integers together.

    Args:
        a: The first integer.
        b: The second integer.
    """
    return a + b


def main() -> None:
    result = agent.run_sync("What is 12 plus 30? Use the tool to compute it.")
    print("Output:", result.output)


if __name__ == "__main__":
    main()
