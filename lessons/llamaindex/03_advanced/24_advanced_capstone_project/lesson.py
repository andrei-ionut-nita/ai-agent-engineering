"""
Lesson 24 (capstone): Multi-document agentic RAG with structured output.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/03_advanced/24_advanced_capstone_project/lesson.py

This is the last lesson in the course, and it ties together the pieces
from every tier: Settings (Lesson 3), VectorStoreIndex and QueryEngine
(Lessons 4-5), tools (Lesson 14), a real agent that decides which of
several document sets to search (Lessons 15-17's territory), and
structured output (Lesson 10), now returned by the AGENT itself rather
than a single query engine. Two separate corpora, Nimbus HR/expense
policies and Nimbus engineering/product documentation, are each wrapped
as a QueryEngineTool, and a FunctionAgent picks which one(s) a question
actually needs, then hands back a validated Pydantic object instead of
free text.
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.tools import QueryEngineTool
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from pydantic import BaseModel, Field

load_dotenv()
API_KEY = os.environ["GOOGLE_API_KEY"]

POLICY_DATA_DIR = Path(__file__).parent.parent.parent / "01_beginner" / "02_documents_and_nodes" / "data"
ENGINEERING_DATA_DIR = Path(__file__).parent.parent.parent / "02_intermediate" / "13_multi_document_indexes" / "data"

Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)


# The structured shape every agent answer gets coerced into, this course's
# Lesson 10 pattern (output_cls / as_structured_llm), applied here to a
# whole agent's final answer instead of one query engine's response.
class NimbusAnswer(BaseModel):
    answer: str = Field(description="A concise, direct answer to the user's question")
    document_sets_used: list[str] = Field(
        description="Which document set(s) were searched to answer this: "
        "'hr_policies', 'engineering_docs', both, or neither if answered from general knowledge"
    )
    needs_human_followup: bool = Field(
        description="True if the answer is incomplete, uncertain, or the "
        "documents didn't fully cover the question and a human should verify it"
    )


def build_query_engine_tool(data_dir: Path, name: str, description: str) -> QueryEngineTool:
    """Build a small VectorStoreIndex over one document folder and wrap it
    as a QueryEngineTool, the same building blocks from Lessons 4-5 and 14,
    combined into one reusable function since this lesson needs it twice."""
    documents = SimpleDirectoryReader(str(data_dir)).load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine(similarity_top_k=2)
    return QueryEngineTool.from_defaults(
        query_engine=query_engine,
        name=name,
        description=description,
    )


def main() -> None:
    policy_tool = build_query_engine_tool(
        POLICY_DATA_DIR,
        name="hr_policies",
        description=(
            "Search Nimbus Robotics' HR policies: vacation, remote work, "
            "and expense reimbursement. Use for employee-facing questions."
        ),
    )
    engineering_tool = build_query_engine_tool(
        ENGINEERING_DATA_DIR,
        name="engineering_docs",
        description=(
            "Search Nimbus Robotics' engineering handbook (code review, "
            "on-call, deploys, testing) and the Cobalt-1 product FAQ "
            "(battery life, specs, connectivity). Use for engineering or "
            "product questions."
        ),
    )

    # FunctionAgent, the same agent class this course's Lessons 15-17
    # build up in depth: it reasons over which tool(s) to call, calls
    # them, and can loop if one call's result suggests it needs another.
    # output_cls swaps its final response for a validated NimbusAnswer
    # instead of free text, the agent-level equivalent of Lesson 10's
    # query-engine-level output_cls.
    agent = FunctionAgent(
        tools=[policy_tool, engineering_tool],
        llm=Settings.llm,
        system_prompt=(
            "You are Nimbus Robotics' internal assistant. Use hr_policies "
            "for employee policy questions and engineering_docs for "
            "engineering or product questions. Some questions may need both."
        ),
        output_cls=NimbusAnswer,
    )

    questions = [
        "How many vacation days can a new hire use in their first 90 days, "
        "and how long does the Cobalt-1's battery last?",
    ]

    async def run_all() -> None:
        for question in questions:
            result = await agent.run(question)
            parsed: NimbusAnswer = result.get_pydantic_model(NimbusAnswer)

            print(f"Q: {question}\n")
            print(f"answer: {parsed.answer}")
            print(f"document_sets_used: {parsed.document_sets_used}")
            print(f"needs_human_followup: {parsed.needs_human_followup}")
            print()

    asyncio.run(run_all())

    print("This is the last lesson in this course.")
    print(
        "Every piece used above, Settings, VectorStoreIndex, QueryEngine, "
        "QueryEngineTool, FunctionAgent, and structured output, was built "
        "up one lesson at a time across all three tiers."
    )


if __name__ == "__main__":
    main()
