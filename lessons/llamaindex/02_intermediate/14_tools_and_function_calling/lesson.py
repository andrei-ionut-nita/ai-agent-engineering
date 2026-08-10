"""
Lesson 14: Tools and function calling, before there's a full agent.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/02_intermediate/14_tools_and_function_calling/lesson.py

This lesson is the bridge between "an LLM that just talks" (Lesson 3) and
"an agent that reasons in a loop" (Lesson 15). A FunctionTool wraps a plain
Python function so an LLM can decide to call it, and Settings.llm.predict_and_call()
is the simplest way to let the LLM pick a tool, call it, and hand back the
result, no agent loop, no multi-step reasoning yet, one tool call and done.
"""

import os

from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.core.tools import FunctionTool
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()
API_KEY = os.environ["GOOGLE_API_KEY"]

Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)


# A small, deterministic, fake lookup, no real API call. In a real system
# this might hit a database or an internal service; the point of this
# lesson is the wiring, not the data source, so a hardcoded dict is enough.
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


def main() -> None:
    # FunctionTool.from_defaults() wraps a plain Python function as
    # something an LLM can call. It reads the function's name, its
    # docstring, and its type-annotated parameters to build the tool's
    # schema automatically, the same "introspect a Python function" idea
    # LangChain's @tool decorator uses, just spelled as a classmethod here
    # instead of a decorator.
    expense_tool = FunctionTool.from_defaults(fn=get_expense_limit)

    print("Tool built from a plain Python function:")
    print(f"  name: {expense_tool.metadata.name}")
    print(f"  description: {expense_tool.metadata.description}")

    # predict_and_call() is the simplest tool-calling mechanism LlamaIndex
    # offers, one LLM call decides whether (and how) to call a tool, then
    # the tool actually runs, and the result comes back as an
    # AgentChatResponse. There's no loop here: it calls at most the tools
    # the model asks for in this single turn and returns, it does not
    # reason step by step the way a full agent (Lesson 15) does.
    question = "What is Nimbus Robotics' reimbursement limit for hotel expenses?"
    response = Settings.llm.predict_and_call(
        [expense_tool],
        question,
        verbose=True,
    )

    print(f"\nQuestion: {question}")
    print(f"Answer: {response.response}")

    # response.sources holds the raw ToolOutput(s) produced along the way,
    # useful for showing exactly what a tool returned, separate from
    # however the LLM chose to phrase its final answer.
    print(f"\nRaw tool output: {response.sources[0].content}")


if __name__ == "__main__":
    main()
