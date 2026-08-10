"""
Lesson 15: A real agent, FunctionAgent.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/02_intermediate/15_agents_with_llamaindex/lesson.py

Lesson 14's predict_and_call() made exactly one tool-calling decision and
stopped. FunctionAgent is the real thing: it runs a loop, deciding on each
step whether to call a tool, call another tool, or give a final answer,
until it thinks it has enough information to answer the user. This is
LlamaIndex's equivalent of LangChain's create_agent, both build on the
model's native function-calling support (Gemini supports this natively).
"""

import asyncio
import os

from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.tools import FunctionTool
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()
API_KEY = os.environ["GOOGLE_API_KEY"]

Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)


# Same fake, hardcoded lookup as Lesson 14, reused here so this lesson can
# focus on what's new: the agent loop around the tool, not the tool itself.
EXPENSE_LIMITS = {
    "meals": "50 EUR per day",
    "hotel": "150 EUR per night",
    "flights": "800 EUR per booking, economy class",
    "software": "300 EUR per year, per employee",
}


def get_expense_limit(category: str) -> str:
    """Look up Nimbus Robotics' reimbursement limit for an expense category.

    Args:
        category: The expense category, e.g. "meals", "hotel", "flights", or "software".
    """
    category_key = category.strip().lower()
    if category_key in EXPENSE_LIMITS:
        return f"The reimbursement limit for {category_key} is {EXPENSE_LIMITS[category_key]}."
    return f"No reimbursement limit is on file for '{category}'."


def convert_eur_to_usd(amount_eur: float) -> str:
    """Convert an amount in EUR to USD using a fixed, made-up exchange rate.

    Args:
        amount_eur: The amount in euros to convert.
    """
    # A fixed rate, not a real API call, deterministic and free, this
    # lesson is about the agent loop, not real currency data.
    rate = 1.08
    return f"{amount_eur} EUR is approximately {amount_eur * rate:.2f} USD (at a fixed rate of {rate})."


async def run_agent() -> None:
    # FunctionAgent is LlamaIndex's standard single-agent, tool-calling
    # agent, built on the llama-index-workflows engine. Unlike Lesson 14's
    # predict_and_call(), which makes one tool decision and stops,
    # FunctionAgent runs take_step() in a loop internally: read the
    # conversation so far, decide whether to call a tool, run it if so,
    # feed the result back in, and repeat until it produces a final answer
    # with no further tool calls.
    agent = FunctionAgent(
        tools=[
            FunctionTool.from_defaults(fn=get_expense_limit),
            FunctionTool.from_defaults(fn=convert_eur_to_usd),
        ],
        llm=Settings.llm,
        system_prompt=(
            "You are a Nimbus Robotics expense assistant. Use the "
            "get_expense_limit tool to look up reimbursement limits, and "
            "convert_eur_to_usd when a question needs a USD figure. Keep "
            "answers short."
        ),
    )

    # FunctionAgent (like every LlamaIndex workflow agent) is async: .run()
    # returns a WorkflowHandler, which is itself awaitable, so it must be
    # awaited to actually execute the loop and get a final result back.
    # A synchronous script therefore needs asyncio.run() around an async
    # entry point, which is why this lesson's main() is split into a sync
    # wrapper and this async function.
    question = (
        "What is the hotel expense limit, and what is that limit in USD?"
    )
    response = await agent.run(user_msg=question)

    print(f"Question: {question}")
    # The result is an AgentOutput; str() on it returns the final message
    # text, the same content as response.response.content.
    print(f"\nFinal answer:\n  {response}")


def main() -> None:
    asyncio.run(run_agent())


if __name__ == "__main__":
    main()
