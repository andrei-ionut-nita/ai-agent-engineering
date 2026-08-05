"""
Lesson 15: reading experiment results back into Python.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langsmith/02_intermediate/15_playground_experiments/lesson.py

Note: LangSmith also has a no-code Playground in the UI, for trying
prompt/model changes by hand against a dataset without writing Python.
This lesson focuses on the SDK side: pulling an experiment's results
back down for your own analysis, useful whether the experiment was
produced by evaluate() (Lessons 9-12) or by the Playground.
"""

import time

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import Client, traceable
from langsmith.evaluation import evaluate

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
client = Client()

DATASET_NAME = "langsmith-course-rag-qa"

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


def keyword_overlap(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    reference_words = set(reference_outputs["answer"].lower().split())
    answer_words = set(outputs["answer"].lower().split())
    overlap = reference_words & answer_words
    score = len(overlap) / len(reference_words) if reference_words else 0.0
    return {"key": "keyword_overlap", "score": round(score, 2)}


def target(inputs: dict) -> dict:
    return {"answer": rag_answer(inputs["question"])}


def fetch_test_results_with_retry(experiment_name: str, feedback_column: str, attempts: int = 8):
    # evaluate() returning doesn't guarantee the experiment (or its
    # per-run feedback_stats, which is where evaluator scores come
    # from) has finished indexing server-side yet. get_test_results can
    # briefly raise, or come back missing the feedback column entirely,
    # if called immediately after. An ordinary eventual-consistency gap,
    # not a bug, when a script reads data it just finished writing.
    # Retrying with a short, growing wait rides that gap out instead of
    # guessing a fixed delay that might be too short.
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
        evaluators=[keyword_overlap],
        experiment_prefix="rag-readback",
    )
    experiment_name = results.experiment_name
    print(f"Ran experiment: {experiment_name}")

    # get_test_results pulls an experiment's full results (inputs,
    # outputs, reference outputs, and every evaluator's score) back down
    # as a pandas DataFrame, for whatever analysis Python can do that
    # the UI's tables don't offer directly, custom charts, filters,
    # joining against other data, and so on.
    dataframe = fetch_test_results_with_retry(experiment_name, "feedback.keyword_overlap")
    print(f"\nColumns available: {list(dataframe.columns)}")
    print(f"\nAverage keyword_overlap: {dataframe['feedback.keyword_overlap'].mean():.2f}")
    print(dataframe[["input.question", "outputs.answer", "feedback.keyword_overlap"]])


if __name__ == "__main__":
    main()
