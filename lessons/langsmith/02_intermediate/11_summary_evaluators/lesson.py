"""
Lesson 11: scoring a whole experiment, not just one example at a time.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langsmith/02_intermediate/11_summary_evaluators/lesson.py
"""

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import traceable
from langsmith.evaluation import evaluate
from langsmith.schemas import Example, Run

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


# A per-example evaluator, same shape as Lesson 10, kept here so this
# experiment still gets a per-result score, not just a summary one.
def keyword_overlap(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    reference_words = set(reference_outputs["answer"].lower().split())
    answer_words = set(outputs["answer"].lower().split())
    overlap = reference_words & answer_words
    score = len(overlap) / len(reference_words) if reference_words else 0.0
    return {"key": "keyword_overlap", "score": round(score, 2)}


# A summary evaluator receives every run and every example from the
# whole experiment at once, not one at a time, so it can compute
# something a per-example evaluator can't: an aggregate across all of
# them, here, the fraction of examples that cleared a threshold.
def pass_rate(runs: list[Run], examples: list[Example]) -> dict:
    reference_by_id = {example.id: example.outputs["answer"] for example in examples}
    passed = 0
    for run in runs:
        reference = reference_by_id[run.reference_example_id]
        reference_words = set(reference.lower().split())
        answer_words = set(run.outputs["answer"].lower().split())
        overlap = len(reference_words & answer_words) / len(reference_words)
        if overlap >= 0.5:
            passed += 1
    return {"key": "pass_rate", "score": passed / len(runs)}


def main() -> None:
    results = evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[keyword_overlap],
        summary_evaluators=[pass_rate],
        experiment_prefix="rag-summarized",
        description="RAG app with a per-example score and an experiment-wide pass rate.",
    )
    print(f"Experiment: {results.experiment_name}")
    print("Per-example scores and the overall pass rate are visible in the UI.")


if __name__ == "__main__":
    main()
