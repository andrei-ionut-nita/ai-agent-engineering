"""
Lesson 19 (Checkpoint): a multi-agent support triage system, with evals.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/02_intermediate/19_intermediate_checkpoint_project/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root.
"""

import asyncio
from dataclasses import dataclass

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import Evaluator, EvaluatorContext

load_dotenv()


class BillingResponse(BaseModel):
    kind: str = "billing"
    message: str


class TechnicalResponse(BaseModel):
    kind: str = "technical"
    message: str


billing_agent = Agent(
    "google:gemini-3.5-flash-lite",
    output_type=BillingResponse,
    system_prompt="You handle billing questions. Respond briefly.",
)
technical_agent = Agent(
    "google:gemini-3.5-flash-lite",
    output_type=TechnicalResponse,
    system_prompt="You handle technical support questions. Respond briefly.",
)

triage_agent = Agent(
    "google:gemini-3.5-flash-lite",
    output_type=BillingResponse | TechnicalResponse,
    system_prompt=(
        "Route the user's support message to handle_billing or "
        "handle_technical, whichever fits, and return its result."
    ),
)


@triage_agent.tool
def handle_billing(ctx: RunContext[None], message: str) -> BillingResponse:
    """Handle a billing-related support message.

    Args:
        message: The user's original message.
    """
    return billing_agent.run_sync(message, usage=ctx.usage).output


@triage_agent.tool
def handle_technical(ctx: RunContext[None], message: str) -> TechnicalResponse:
    """Handle a technical support message.

    Args:
        message: The user's original message.
    """
    return technical_agent.run_sync(message, usage=ctx.usage).output


async def triage(message: str) -> str:
    """Run triage and return just the routed kind, for eval scoring."""
    result = await triage_agent.run(message)
    return result.output.kind


@dataclass
class MatchesKind(Evaluator):
    def evaluate(self, ctx: EvaluatorContext) -> bool:
        return ctx.output == ctx.expected_output


dataset = Dataset(
    name="support_triage",
    cases=[
        Case(
            name="overcharge",
            inputs="I was charged twice for my subscription this month.",
            expected_output="billing",
        ),
        Case(
            name="crash",
            inputs="The app crashes every time I try to open it.",
            expected_output="technical",
        ),
        Case(
            name="refund",
            inputs="How do I get a refund for last week's payment?",
            expected_output="billing",
        ),
    ],
    evaluators=[MatchesKind()],
)


async def main() -> None:
    print("Sample routed responses:")
    for message in [
        "I was charged twice for my subscription this month.",
        "The app crashes every time I try to open it.",
    ]:
        result = await triage_agent.run(message)
        print(f"  [{result.output.kind}] {result.output.message}")

    print("\nEval report:")
    report = await dataset.evaluate(triage, max_concurrency=1)
    print(report)


if __name__ == "__main__":
    asyncio.run(main())
