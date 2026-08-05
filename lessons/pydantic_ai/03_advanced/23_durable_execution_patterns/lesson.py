"""
Lesson 23: durable execution patterns.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/03_advanced/23_durable_execution_patterns/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root.
"""

from dataclasses import dataclass, field

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

load_dotenv()


@dataclass
class PaymentDeps:
    processed: set[str] = field(default_factory=set)


agent = Agent(
    "google:gemini-3.5-flash-lite",
    deps_type=PaymentDeps,
    system_prompt=(
        "You process payments. Always call charge_card with a stable "
        "idempotency_key derived from the order id, e.g. 'order-123'."
    ),
)


@agent.tool
def charge_card(
    ctx: RunContext[PaymentDeps], idempotency_key: str, amount: float
) -> str:
    """Charge a card for an amount, safe to call more than once.

    Args:
        idempotency_key: A stable identifier for this exact charge.
        amount: The amount in dollars to charge.
    """
    if idempotency_key in ctx.deps.processed:
        return f"Already processed '{idempotency_key}', not charging again."
    ctx.deps.processed.add(idempotency_key)
    return f"Charged ${amount:.2f} (key={idempotency_key})."


def main() -> None:
    deps = PaymentDeps()

    print("First charge for order-123:")
    result = agent.run_sync(
        "Charge $42.00 for order-123.", deps=deps
    )
    print(" ", result.output)

    print("\nRetrying the exact same request (simulating a client retry):")
    result = agent.run_sync(
        "Charge $42.00 for order-123.", deps=deps
    )
    print(" ", result.output)

    print(f"\nOperations actually processed: {deps.processed}")


if __name__ == "__main__":
    main()
