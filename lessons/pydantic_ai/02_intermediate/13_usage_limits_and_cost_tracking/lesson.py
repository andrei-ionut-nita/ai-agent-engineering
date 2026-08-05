"""
Lesson 13: usage limits and cost tracking.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/02_intermediate/13_usage_limits_and_cost_tracking/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root.
"""

from dotenv import load_dotenv
from pydantic_ai import Agent, UsageLimits
from pydantic_ai.exceptions import UsageLimitExceeded

load_dotenv()

agent = Agent("google:gemini-3.5-flash-lite")


def main() -> None:
    result = agent.run_sync("Say hi in one word.")
    print("Output:", result.output)
    print("Usage:", result.usage)

    print("\nSetting an unreasonably low token limit on purpose:")
    try:
        agent.run_sync(
            "Say hi in one word.",
            usage_limits=UsageLimits(total_tokens_limit=1),
        )
    except UsageLimitExceeded as error:
        print("Caught UsageLimitExceeded:", error)


if __name__ == "__main__":
    main()
