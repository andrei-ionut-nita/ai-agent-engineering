"""
Lesson 17: Intermediate checkpoint, an agent with a RAG tool and a plain
function tool, combined.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/02_intermediate/17_intermediate_checkpoint_project/lesson.py

This lesson doesn't introduce anything new, it recombines Lessons 10-16's
pieces into one small agent, which is the point of a checkpoint:

  - Lesson 4/5's VectorStoreIndex + QueryEngine, wrapped as a
    QueryEngineTool (a query engine is itself just a tool an agent can
    call, the same idea Lesson 16 used, just one tool here instead of two).
  - Lesson 14's FunctionTool, wrapping a plain Python function.
  - Lesson 15's FunctionAgent, choosing between them per question.

The agent below has two tools, one that can answer questions about Nimbus
Robotics' policies (RAG-as-a-tool) and one that does a trivial numeric
lookup that has nothing to do with documents at all. Which tool the right
answer requires is different per question, and picking correctly is the
whole exercise.
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.tools import FunctionTool, QueryEngineTool, ToolMetadata
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()
API_KEY = os.environ["GOOGLE_API_KEY"]

DATA_DIR = Path(__file__).parent.parent.parent / "01_beginner" / "02_documents_and_nodes" / "data"

Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)


# A trivial, deterministic function tool, unrelated to the document data,
# so the agent genuinely has to pick between "look this up in the
# policies" and "compute this directly."
def days_until_review(months_employed: int) -> str:
    """Compute how many days until an employee's next performance review.

    Nimbus Robotics runs performance reviews every 6 months. This is a
    plain calculation, not a lookup, no document contains this number.

    Args:
        months_employed: How many whole months the employee has been employed.
    """
    review_cycle_months = 6
    months_until_next = review_cycle_months - (months_employed % review_cycle_months)
    if months_until_next == review_cycle_months:
        months_until_next = 0
    return f"{months_until_next} month(s) until the next performance review (reviews happen every {review_cycle_months} months)."


def build_policy_tool() -> QueryEngineTool:
    # Same pattern as Lesson 4/5 (VectorStoreIndex.from_documents +
    # as_query_engine) and Lesson 16 (wrapped as a QueryEngineTool), now
    # over all three Nimbus policy files instead of just one, since this
    # tool needs to answer whatever policy question comes up, not just one
    # topic.
    documents = SimpleDirectoryReader(str(DATA_DIR)).load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    return QueryEngineTool(
        query_engine=query_engine,
        metadata=ToolMetadata(
            name="nimbus_policy_search",
            description=(
                "Answers questions about Nimbus Robotics' written policies: "
                "vacation, remote work, and expense reimbursement. Use this "
                "for anything a policy document would contain."
            ),
        ),
    )


async def run_agent() -> None:
    policy_tool = build_policy_tool()
    review_tool = FunctionTool.from_defaults(fn=days_until_review)

    # One FunctionAgent, two tools of genuinely different kinds: one is a
    # QueryEngine (retrieval + synthesis over real documents), the other is
    # a plain Python function (pure computation, no documents involved).
    # From the agent's perspective both are just AsyncBaseTool objects with
    # a name and a description, it decides which to call the same way
    # either way, by reading each tool's description against the question.
    agent = FunctionAgent(
        tools=[policy_tool, review_tool],
        llm=Settings.llm,
        system_prompt=(
            "You are a Nimbus Robotics HR assistant. Use nimbus_policy_search "
            "for questions about written policy, and days_until_review for "
            "questions about when someone's next performance review is. "
            "Keep answers short."
        ),
    )

    questions = [
        "How many days of paid parental leave does Nimbus Robotics offer?",
        "An employee has been here 8 months. How long until their next performance review?",
    ]

    for question in questions:
        response = await agent.run(user_msg=question)
        print(f"Question: {question}")
        print(f"Answer: {response}\n")


def main() -> None:
    asyncio.run(run_agent())


if __name__ == "__main__":
    main()
