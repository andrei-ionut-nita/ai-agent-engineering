"""
Lesson 9: streaming output with run_stream.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/01_beginner/09_streaming_output/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root.
"""

import asyncio

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent

load_dotenv()


class CityFact(BaseModel):
    city: str
    country: str


text_agent = Agent("google:gemini-3.5-flash-lite")
structured_agent = Agent("google:gemini-3.5-flash-lite", output_type=CityFact)


async def main() -> None:
    print("Streaming plain text:")
    async with text_agent.run_stream("Count from 1 to 5, one number per line.") as result:
        async for chunk in result.stream_output():
            print("  ", repr(chunk))

    print("\nStreaming structured output:")
    async with structured_agent.run_stream("Tell me about Tokyo.") as result:
        async for partial in result.stream_output():
            print("  ", partial)


if __name__ == "__main__":
    asyncio.run(main())
