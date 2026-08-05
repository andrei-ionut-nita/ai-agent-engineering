"""
Lesson 16: Intermediate Checkpoint - Dataset + Evaluator for the RAG App.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langsmith/02_intermediate/16_intermediate_checkpoint_project/lesson.py
"""

import time

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import Client, traceable
from langsmith.evaluation import evaluate
from langsmith.schemas import Example, Run

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
client = Client()

DATASET_NAME = "langsmith-course-rag-qa"
PROMPT_NAME = "langsmith-course-rag-prompt"

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
    prompt = client.pull_prompt(PROMPT_NAME)
    context = "\n".join(retrieve(question))
    response = (prompt | model).invoke({"context": context, "question": question})
    return response.text


def target(inputs: dict) -> dict:
    return {"answer": rag_answer(inputs["question"])}


def keyword_overlap(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    reference_words = set(reference_outputs["answer"].lower().split())
    answer_words = set(outputs["answer"].lower().split())
    overlap = reference_words & answer_words
    score = len(overlap) / len(reference_words) if reference_words else 0.0
    return {"key": "keyword_overlap", "score": round(score, 2)}


def is_concise(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    return {"key": "is_concise", "score": len(outputs["answer"].split()) <= 25}


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


def fetch_test_results_with_retry(experiment_name: str, feedback_column: str, attempts: int = 8):
    # evaluate() returning doesn't guarantee the experiment's per-run
    # feedback has finished indexing server-side yet (Lesson 15), retry
    # with a short, growing wait until the column we need shows up.
    for attempt in range(attempts):
        try:
            dataframe = client.get_test_results(project_name=experiment_name)
            if feedback_column in dataframe.columns:
                return dataframe
        except Exception:
            pass
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(
        f"Experiment '{experiment_name}' never finished indexing '{feedback_column}'."
    )


def main() -> None:
    results = evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[keyword_overlap, is_concise],
        summary_evaluators=[pass_rate],
        experiment_prefix="rag-checkpoint",
        description="Intermediate checkpoint: full evaluation of the RAG app.",
    )

    dataframe = fetch_test_results_with_retry(results.experiment_name, "feedback.keyword_overlap")
    print(f"Experiment: {results.experiment_name}\n")
    print(dataframe[[
        "input.question",
        "outputs.answer",
        "feedback.keyword_overlap",
        "feedback.is_concise",
    ]])
    print(f"\nAverage keyword_overlap: {dataframe['feedback.keyword_overlap'].mean():.2f}")


if __name__ == "__main__":
    main()
