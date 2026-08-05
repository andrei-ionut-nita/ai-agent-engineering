"""
Lesson 7: tools that read RunContext.deps.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/01_beginner/07_tool_with_deps/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root.
"""

from dataclasses import dataclass, field

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

load_dotenv()


@dataclass
class AppDeps:
    notes: dict[str, str] = field(default_factory=dict)


agent = Agent("google:gemini-3.5-flash-lite", deps_type=AppDeps)


@agent.tool
def save_note(ctx: RunContext[AppDeps], title: str, body: str) -> str:
    """Save a note under a title.

    Args:
        title: A short title for the note.
        body: The note's content.
    """
    ctx.deps.notes[title] = body
    return f"Saved note '{title}'."


def main() -> None:
    deps = AppDeps()
    result = agent.run_sync(
        "Save a note titled 'groceries' with the body 'milk, eggs, bread'.",
        deps=deps,
    )
    print("Output:", result.output)
    print("Notes after the run:", deps.notes)


if __name__ == "__main__":
    main()
