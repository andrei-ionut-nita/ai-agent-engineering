"""
Lesson 8: output validators and ModelRetry.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/01_beginner/08_output_validators_and_retries/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root.
"""

from dotenv import load_dotenv
from pydantic_ai import Agent, ModelRetry, RunContext

load_dotenv()

agent = Agent("google:gemini-3.5-flash-lite", output_type=int)


@agent.output_validator
def must_be_positive(ctx: RunContext[None], output: int) -> int:
    if output <= 0:
        raise ModelRetry("The number must be positive. Try again.")
    return output


def main() -> None:
    result = agent.run_sync("Give me a positive integer between 1 and 10.")
    print("Output:", result.output)
    print("Output type:", type(result.output))


if __name__ == "__main__":
    main()
