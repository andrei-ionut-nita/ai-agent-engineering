"""
Lesson 3: structured output with output_type.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/01_beginner/03_structured_output_with_output_type/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root.
"""

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent

load_dotenv()


class CityFact(BaseModel):
    city: str
    country: str
    population_millions: float


agent = Agent("google:gemini-3.5-flash-lite", output_type=CityFact)


def main() -> None:
    result = agent.run_sync("Tell me about Paris.")

    fact = result.output
    print("Output type:", type(fact))
    print("City:", fact.city)
    print("Country:", fact.country)
    print("Population (millions):", fact.population_millions)


if __name__ == "__main__":
    main()
