"""
Lesson 4: system prompts, static and dynamic.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/01_beginner/04_system_prompts/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root.
"""

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

load_dotenv()

agent = Agent(
    "google:gemini-3.5-flash-lite",
    deps_type=str,
    system_prompt="You are a terse pirate. Answer in one short sentence.",
)


@agent.system_prompt
def add_persona(ctx: RunContext[str]) -> str:
    return f"You are speaking to {ctx.deps}. Address them by name."


def main() -> None:
    result = agent.run_sync("What's the weather like today?", deps="Nolan")
    print("Output:", result.output)


if __name__ == "__main__":
    main()
