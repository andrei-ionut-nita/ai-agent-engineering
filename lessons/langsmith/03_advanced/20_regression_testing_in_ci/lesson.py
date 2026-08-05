"""
Lesson 20: failing a build when an experiment's score regresses.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langsmith/03_advanced/20_regression_testing_in_ci/lesson.py

Try it, then intentionally break the retriever below (e.g. make it
always return an empty list) and run it again, watch it exit non-zero.
"""

import sys

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import Client, traceable
from langsmith.evaluation import evaluate
from langsmith.schemas import Example, Run

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
client = Client()

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

# The "checked-in" baseline: the lowest pass rate this app is allowed to
# score before a CI run should fail. In a real project this number
# would live in the repo (a config file, or a constant like this one),
# updated deliberately whenever a genuine improvement raises the bar.
BASELINE_PASS_RATE = 0.60


def target(inputs: dict) -> dict:
    return {"answer": rag_answer(inputs["question"])}


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
        summary_evaluators=[pass_rate],
        experiment_prefix="rag-ci-check",
    )

    # Reading the project (LangSmith's internal name for an experiment)
    # back gives feedback_stats, a dict of every feedback/evaluator key
    # to its aggregate stats, but summary evaluator scores attach to the
    # experiment itself (run_id=None), not to any individual run, so
    # they don't show up there. list_feedback, scoped to this
    # experiment's session and this feedback key, is how the summary
    # evaluator's own score gets back into plain Python.
    project = client.read_project(project_name=results.experiment_name)
    summary_feedback = list(
        client.list_feedback(sessions=[str(project.id)], feedback_key=["pass_rate"])
    )
    current_score = summary_feedback[0].score

    print(f"Experiment: {results.experiment_name}")
    print(f"pass_rate: {current_score:.2f} (baseline: {BASELINE_PASS_RATE:.2f})")

    if current_score < BASELINE_PASS_RATE:
        print("REGRESSION: pass_rate fell below the baseline. Failing the build.")
        sys.exit(1)

    print("No regression, build passes.")


if __name__ == "__main__":
    main()
