"""
Lesson 10: writing evaluator functions that score each result.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langsmith/02_intermediate/10_custom_evaluators/lesson.py
"""

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import traceable
from langsmith.evaluation import evaluate

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

DOCS = {
    "langchain": "LangChain is a framework for building LLM applications with a shared interface across model providers.",
    "langgraph": "LangGraph is a library for building stateful, graph-based agents on top of LangChain.",
    "langsmith": "LangSmith is a platform for tracing, evaluating, and monitoring LLM applications in development and production.",
}


@traceable(run_type="retriever")
def retrieve(question: str) -> list[str]:
    matches = [text for key, text in DOCS.items() if key in question.lower()]
    return matches or list(DOCS.values())


@traceable(run_type="chain")
def rag_answer(question: str) -> str:
    context = "\n".join(retrieve(question))
    response = model.invoke(
        f"Using only this context, answer in one short sentence.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}"
    )
    return response.text


DATASET_NAME = "langsmith-course-rag-qa"


def target(inputs: dict) -> dict:
    return {"answer": rag_answer(inputs["question"])}


# An evaluator is a plain function: inputs (what the example asked),
# outputs (what target() actually produced), reference_outputs (the
# dataset's expected answer). It returns a dict with a "key" (the
# metric's name) and a "score", both shown per-result in the UI.
def keyword_overlap(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    reference_words = set(reference_outputs["answer"].lower().split())
    answer_words = set(outputs["answer"].lower().split())
    overlap = reference_words & answer_words
    score = len(overlap) / len(reference_words) if reference_words else 0.0
    return {"key": "keyword_overlap", "score": round(score, 2)}


# A second, independent evaluator. evaluate() runs every evaluator you
# give it against every result, so a single experiment can be scored on
# several unrelated criteria at once.
def is_concise(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    word_count = len(outputs["answer"].split())
    return {"key": "is_concise", "score": word_count <= 25}


def main() -> None:
    results = evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[keyword_overlap, is_concise],
        experiment_prefix="rag-scored",
        description="RAG app scored on keyword overlap and conciseness.",
    )
    print(f"Experiment: {results.experiment_name}")

    for result in results:
        question = result["example"].inputs["question"]
        # Each entry in "results" is an EvaluationResult object (attribute
        # access), not a dict, unlike "example"/"run" above.
        scores = {ev.key: ev.score for ev in result["evaluation_results"]["results"]}
        print(f"- {question}\n  scores: {scores}")


if __name__ == "__main__":
    main()
