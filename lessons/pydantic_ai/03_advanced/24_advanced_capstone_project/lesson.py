"""
Lesson 24 (Capstone): an order-total assistant, end to end.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/03_advanced/24_advanced_capstone_project/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root. Launches
server.py (in this same folder) as an MCP subprocess over stdio.
"""

import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.mcp import MCPToolset, StdioTransport
from pydantic_ai.models.fallback import FallbackModel
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import Evaluator, EvaluatorContext

load_dotenv()

SERVER_SCRIPT = Path(__file__).parent / "server.py"

CATALOG = {
    "widget": 9.99,
    "gadget": 24.50,
    "gizmo": 4.25,
}


class OrderResult(BaseModel):
    items: list[str]
    total: float
    note: str


@dataclass
class CatalogDeps:
    prices: dict[str, float]


transport = StdioTransport(command=sys.executable, args=[str(SERVER_SCRIPT)])
toolset = MCPToolset(transport)

fallback_model = FallbackModel(
    "google:gemini-9.9-does-not-exist",
    "google:gemini-3.5-flash-lite",
)

agent = Agent(
    fallback_model,
    deps_type=CatalogDeps,
    output_type=OrderResult,
    toolsets=[toolset],
    system_prompt=(
        "You compute order totals. Look up each item's price with "
        "get_price, then use the add and multiply MCP tools to compute "
        "the total, never do arithmetic yourself. Return items, the "
        "final total, and a one-sentence note."
    ),
)


@agent.tool
def get_price(ctx: RunContext[CatalogDeps], item: str) -> float:
    """Look up the catalog price for an item.

    Args:
        item: The item name, lowercase.
    """
    return ctx.deps.prices[item.lower()]


async def order_total(order_text: str) -> float:
    async with agent:
        result = await agent.run(order_text, deps=CatalogDeps(prices=CATALOG))
        return result.output.total


@dataclass
class CloseEnough(Evaluator):
    def evaluate(self, ctx: EvaluatorContext) -> bool:
        return abs(ctx.output - ctx.expected_output) < 0.01


dataset = Dataset(
    name="order_totals",
    cases=[
        Case(
            name="two_widgets",
            inputs="2 widgets",
            expected_output=2 * CATALOG["widget"],
        ),
        Case(
            name="gadget_and_gizmo",
            inputs="1 gadget and 1 gizmo",
            expected_output=CATALOG["gadget"] + CATALOG["gizmo"],
        ),
    ],
    evaluators=[CloseEnough()],
)


async def main() -> None:
    async with agent:
        result = await agent.run(
            "3 widgets and 1 gizmo", deps=CatalogDeps(prices=CATALOG)
        )
    print("Order result:", result.output)

    model_responses = [
        message
        for message in result.all_messages()
        if hasattr(message, "model_name")
    ]
    print("Model that actually answered:", model_responses[-1].model_name)

    print("\nEval report:")
    report = await dataset.evaluate(order_total, max_concurrency=1)
    print(report)


if __name__ == "__main__":
    asyncio.run(main())
