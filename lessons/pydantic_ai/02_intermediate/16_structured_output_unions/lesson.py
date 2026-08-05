"""
Lesson 16: structured output unions.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/02_intermediate/16_structured_output_unions/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root.
"""

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent

load_dotenv()


class WeatherAnswer(BaseModel):
    kind: str = "weather"
    forecast: str


class JokeAnswer(BaseModel):
    kind: str = "joke"
    text: str


agent = Agent(
    "google:gemini-3.5-flash-lite",
    output_type=WeatherAnswer | JokeAnswer,
)


def handle(prompt: str) -> None:
    result = agent.run_sync(prompt)
    match result.output:
        case JokeAnswer(text=text):
            print(f"[{prompt!r}] -> JokeAnswer: {text}")
        case WeatherAnswer(forecast=forecast):
            print(f"[{prompt!r}] -> WeatherAnswer: {forecast}")


def main() -> None:
    handle("Tell me a joke.")
    handle("Will it rain tomorrow in Paris?")


if __name__ == "__main__":
    main()
