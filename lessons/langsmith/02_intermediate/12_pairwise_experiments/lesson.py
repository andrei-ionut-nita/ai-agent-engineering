"""
Lesson 12: comparing two experiments head to head.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langsmith/02_intermediate/12_pairwise_experiments/lesson.py
"""

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import traceable
from langsmith.evaluation import evaluate, evaluate_comparative
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


# Two variants of the same app, differing only in prompt instruction,
# to give this lesson two genuinely different experiments to compare.
@traceable(run_type="chain")
def rag_answer_concise(question: str) -> str:
    context = "\n".join(retrieve(question))
    response = model.invoke(
        f"Using only this context, answer in one short sentence.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}"
    )
    return response.text


@traceable(run_type="chain")
def rag_answer_detailed(question: str) -> str:
    context = "\n".join(retrieve(question))
    response = model.invoke(
        f"Using only this context, answer thoroughly, covering every "
        f"relevant detail from the context.\n\nContext:\n{context}\n\n"
        f"Question: {question}"
    )
    return response.text


DATASET_NAME = "langsmith-course-rag-qa"


# A pairwise evaluator compares runs against each other for the same
# example, rather than against a fixed reference. It returns a "scores"
# dict keyed by run id, here 1.0 for the run judged more concise, 0.0
# for the other.
def prefers_shorter(runs: list[Run], example: Example) -> dict:
    # A run's outputs can occasionally still be None here if it hasn't
    # finished indexing server-side yet (this evaluator runs right after
    # both experiments finish). Treat that run as a tie rather than
    # crashing on it.
    lengths = {
        run.id: len(run.outputs["answer"].split()) if run.outputs else None
        for run in runs
    }
    known = {run_id: length for run_id, length in lengths.items() if length is not None}
    if not known:
        return {"key": "prefers_shorter", "scores": {run_id: 0.5 for run_id in lengths}}
    shortest_id = min(known, key=known.get)
    scores = {run_id: (1.0 if run_id == shortest_id else 0.0) for run_id in known}
    scores.update({run_id: 0.5 for run_id in lengths if run_id not in known})
    return {"key": "prefers_shorter", "scores": scores}


def main() -> None:
    concise_results = evaluate(
        lambda inputs: {"answer": rag_answer_concise(inputs["question"])},
        data=DATASET_NAME,
        experiment_prefix="rag-concise",
    )
    detailed_results = evaluate(
        lambda inputs: {"answer": rag_answer_detailed(inputs["question"])},
        data=DATASET_NAME,
        experiment_prefix="rag-detailed",
    )

    print(f"Experiment A: {concise_results.experiment_name}")
    print(f"Experiment B: {detailed_results.experiment_name}")

    # evaluate_comparative runs the pairwise evaluator once per example,
    # across both named experiments, instead of scoring each in
    # isolation against a fixed reference.
    evaluate_comparative(
        [concise_results.experiment_name, detailed_results.experiment_name],
        evaluators=[prefers_shorter],
    )
    print("Pairwise comparison recorded, view it in the UI next to both experiments.")


if __name__ == "__main__":
    main()
