"""
Lesson 2: your first agent.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/01_beginner/02_first_agent/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root, same as
every langchain lesson.
"""

from dotenv import load_dotenv
from pydantic_ai import Agent

load_dotenv()

agent = Agent("google:gemini-3.5-flash-lite")


def main() -> None:
    result = agent.run_sync("What is the capital of France? Answer in one sentence.")

    print("Output:", result.output)
    print("Output type:", type(result.output))


if __name__ == "__main__":
    main()
