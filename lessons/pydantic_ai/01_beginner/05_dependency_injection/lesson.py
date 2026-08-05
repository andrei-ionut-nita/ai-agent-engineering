"""
Lesson 5: dependency injection with RunContext.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/01_beginner/05_dependency_injection/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root.
"""

from dataclasses import dataclass

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

load_dotenv()


@dataclass
class AppDeps:
    user_name: str
    is_admin: bool


agent = Agent("google:gemini-3.5-flash-lite", deps_type=AppDeps)


@agent.system_prompt
def greet(ctx: RunContext[AppDeps]) -> str:
    role = "an admin" if ctx.deps.is_admin else "a regular user"
    return f"The user's name is {ctx.deps.user_name}, and they are {role}."


def main() -> None:
    result = agent.run_sync(
        "Greet me and tell me what my permission level is.",
        deps=AppDeps(user_name="Nolan", is_admin=False),
    )
    print("Output:", result.output)


if __name__ == "__main__":
    main()
