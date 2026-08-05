"""
Lesson 6: prompts, reusable interaction templates.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/01_beginner/06_prompts/lesson.py
"""

import asyncio

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("code-review-server")


@mcp.prompt()
def code_review(language: str, code: str) -> str:
    """Ask for a structured code review of a snippet."""
    return (
        f"Please review this {language} code for bugs, style issues, "
        f"and possible improvements:\n\n{code}"
    )


async def main() -> None:
    prompts = await mcp.list_prompts()
    print("Registered prompts:")
    for prompt in prompts:
        print(f"  {prompt.name}: {prompt.description}")

    # get_prompt fills in the template's arguments and hands back a
    # list of messages, ready to send to a model.
    result = await mcp.get_prompt(
        "code_review",
        {"language": "python", "code": "print('hello')"},
    )
    print("\nFilled-in prompt messages:")
    for message in result.messages:
        print(f"  [{message.role}] {message.content.text}")


if __name__ == "__main__":
    asyncio.run(main())
