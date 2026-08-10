"""
Lesson 18: Evaluating retrieval, faithfulness and relevancy.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/03_advanced/18_evaluating_retrieval/lesson.py

Every RAG lesson so far has trusted that the QueryEngine's answer is good.
This lesson stops trusting and starts checking, using two of LlamaIndex's
built-in LLM-as-judge evaluators against the Nimbus Robotics policy index
from Lesson 4 (01_beginner/04_first_vector_index).
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.evaluation import FaithfulnessEvaluator, RelevancyEvaluator
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()
API_KEY = os.environ["GOOGLE_API_KEY"]

DATA_DIR = Path(__file__).parent.parent.parent / "01_beginner" / "02_documents_and_nodes" / "data"

Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)


def main() -> None:
    documents = SimpleDirectoryReader(str(DATA_DIR)).load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine(similarity_top_k=2)

    # Two different LLM-as-judge evaluators, each asking a different
    # question about the SAME query/response/context triple:
    #   FaithfulnessEvaluator: is the answer actually supported by the
    #     retrieved context, or did the LLM make something up (hallucinate)?
    #   RelevancyEvaluator: does the retrieved context, together with the
    #     response, actually address the query, or did retrieval fetch the
    #     wrong Nodes entirely?
    # Both default to Settings.llm as the judge if no llm= is passed, the
    # same "one LLM, two jobs" pattern used everywhere else in this course.
    faithfulness_evaluator = FaithfulnessEvaluator()
    relevancy_evaluator = RelevancyEvaluator()

    questions = [
        "How many vacation days can a new hire use in their first 90 days?",
        "What is the reimbursement limit for a hotel stay?",
    ]

    for question in questions:
        response = query_engine.query(question)

        # evaluate_response() takes the query string and the QueryEngine's
        # own Response object, it pulls the retrieved context straight off
        # response.source_nodes, no need to pass contexts by hand.
        faithfulness_result = faithfulness_evaluator.evaluate_response(
            query=question, response=response
        )
        relevancy_result = relevancy_evaluator.evaluate_response(
            query=question, response=response
        )

        print(f"Q: {question}")
        print(f"A: {response.response.strip()}\n")
        print(f"  Faithfulness: {'PASS' if faithfulness_result.passing else 'FAIL'} (score={faithfulness_result.score})")
        print(f"  Relevancy:    {'PASS' if relevancy_result.passing else 'FAIL'} (score={relevancy_result.score})")
        print()


if __name__ == "__main__":
    main()
