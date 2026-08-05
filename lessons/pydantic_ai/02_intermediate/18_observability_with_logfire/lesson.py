"""
Lesson 18: observability with Logfire.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/02_intermediate/18_observability_with_logfire/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root. No Logfire
account is needed: this lesson keeps tracing entirely local.
"""

import logfire
from dotenv import load_dotenv
from pydantic_ai import Agent

load_dotenv()

# local-only tracing: prints spans to the console, sends nothing anywhere.
logfire.configure(send_to_logfire=False)
logfire.instrument_pydantic_ai()

agent = Agent("google:gemini-3.5-flash-lite")


@agent.tool_plain
def add(a: int, b: int) -> int:
    """Add two integers together."""
    return a + b


def main() -> None:
    result = agent.run_sync("What is 12 plus 30? Use the tool.")
    print("\nOutput:", result.output)


if __name__ == "__main__":
    main()
