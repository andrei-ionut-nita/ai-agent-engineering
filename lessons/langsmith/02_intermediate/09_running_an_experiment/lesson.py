"""
Lesson 9: running the RAG app over a whole dataset at once.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langsmith/02_intermediate/09_running_an_experiment/lesson.py

Same small RAG app as Lesson 8 (self-contained here, same as every
lesson in this course), the new part is the bottom of this file.
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


# target() is the shape evaluate() requires: a function taking one
# example's inputs dict, returning a dict of outputs. It's the
# adapter between "however your app's function signature looks" and
# "whatever evaluate() needs to call".
def target(inputs: dict) -> dict:
    return {"answer": rag_answer(inputs["question"])}


def main() -> None:
    # evaluate() runs target() once per example in the dataset, records
    # every run, and groups them under one named "experiment", visible
    # in the UI next to the dataset itself. No evaluators yet, this
    # lesson is only about recording what the app produces; Lesson 10
    # adds automatic scoring.
    results = evaluate(
        target,
        data=DATASET_NAME,
        experiment_prefix="rag-baseline",
        description="Baseline run of the RAG app, no evaluators yet.",
    )
    print(f"Experiment: {results.experiment_name}")

    for result in results:
        question = result["example"].inputs["question"]
        answer = result["run"].outputs["answer"]
        print(f"- {question}\n  -> {answer}")


if __name__ == "__main__":
    main()
