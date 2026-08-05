"""
Lesson 15: pydantic_evals basics.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/02_intermediate/15_pydantic_evals_basics/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root.
"""

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import EqualsExpected

load_dotenv()

agent = Agent(
    "google:gemini-3.5-flash-lite",
    system_prompt="Answer with just the capital city name, nothing else.",
)


def ask_capital(country: str) -> str:
    return agent.run_sync(country).output


dataset = Dataset(
    name="capitals",
    cases=[
        Case(name="france", inputs="France", expected_output="Paris"),
        Case(name="japan", inputs="Japan", expected_output="Tokyo"),
        Case(name="egypt", inputs="Egypt", expected_output="Cairo"),
    ],
    evaluators=[EqualsExpected()],
)


def main() -> None:
    report = dataset.evaluate_sync(ask_capital)
    print(report)


if __name__ == "__main__":
    main()
