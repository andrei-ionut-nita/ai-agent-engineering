"""
Lesson 16: SubQuestionQueryEngine, splitting a compound question across
multiple indexes.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/02_intermediate/16_sub_question_query_engine/lesson.py

Reuses the Nimbus Robotics policy data/ folder from Lesson 2
(01_beginner/02_documents_and_nodes/data/), but this time builds two
SEPARATE indexes, one over vacation_policy.txt, one over expense_policy.txt,
each wrapped as its own QueryEngineTool. A single vacation-policy index has
no way to answer a question about expenses, and vice versa.
SubQuestionQueryEngine solves that: given a compound question, it asks the
LLM to break it into sub-questions, routes each sub-question to whichever
tool's description best matches it, runs them (in parallel by default), and
synthesizes one final answer from all the sub-answers.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.core.question_gen.llm_generators import LLMQuestionGenerator
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()
API_KEY = os.environ["GOOGLE_API_KEY"]

DATA_DIR = Path(__file__).parent.parent.parent / "01_beginner" / "02_documents_and_nodes" / "data"

Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)


def build_query_engine_tool(filename: str, name: str, description: str) -> QueryEngineTool:
    """Build a small, single-document index and wrap it as a QueryEngineTool.

    Each tool's description is what the sub-question generator reads to
    decide which sub-question should go to which tool, so a specific,
    accurate description matters as much as the underlying data.
    """
    documents = SimpleDirectoryReader(input_files=[str(DATA_DIR / filename)]).load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    return QueryEngineTool(
        query_engine=query_engine,
        metadata=ToolMetadata(name=name, description=description),
    )


def main() -> None:
    vacation_tool = build_query_engine_tool(
        "vacation_policy.txt",
        name="vacation_policy",
        description="Answers questions about Nimbus Robotics' vacation days, accrual, and carryover rules.",
    )
    expense_tool = build_query_engine_tool(
        "expense_policy.txt",
        name="expense_policy",
        description="Answers questions about Nimbus Robotics' expense reimbursement thresholds and approval process.",
    )

    # llama-index-question-gen-openai (an OpenAI-function-calling-based
    # question generator) isn't installed in this project, so
    # SubQuestionQueryEngine.from_defaults() would raise ImportError trying
    # to import it as its default. LLMQuestionGenerator is the
    # provider-agnostic fallback: it prompts Settings.llm directly to
    # produce structured sub-questions, no function-calling API required,
    # works with any LLM. Passing it explicitly sidesteps the ImportError.
    question_gen = LLMQuestionGenerator.from_defaults(llm=Settings.llm)

    sub_question_engine = SubQuestionQueryEngine.from_defaults(
        query_engine_tools=[vacation_tool, expense_tool],
        question_gen=question_gen,
        use_async=False,
        verbose=True,
    )

    question = (
        "How many vacation days do new hires get access to during their "
        "first 90 days, and what is the expense reimbursement threshold "
        "that doesn't require pre-approval?"
    )
    response = sub_question_engine.query(question)

    print(f"\nQuestion: {question}")
    print(f"\nFinal synthesized answer:\n  {response}")


if __name__ == "__main__":
    main()
