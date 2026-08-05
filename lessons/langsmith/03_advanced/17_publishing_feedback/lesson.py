"""
Lesson 17: attaching feedback to a run after it's already finished.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langsmith/03_advanced/17_publishing_feedback/lesson.py
"""

import uuid

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import Client, traceable

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


@traceable(run_type="llm")
def judge_helpfulness(question: str, answer: str) -> float:
    verdict = model.invoke(
        f"Question: {question}\nAnswer: {answer}\n\n"
        f"Reply with exactly one word, yes or no: is this answer helpful "
        f"and directly on topic?"
    )
    return 1.0 if "yes" in verdict.text.strip().lower() else 0.0


def main() -> None:
    question = "What is LangSmith used for?"

    # Pre-generating the run id and handing it in via langsmith_extra
    # means we know, before the function even runs, exactly which run
    # to attach feedback to afterward, rather than having to look it up.
    run_id = str(uuid.uuid4())
    answer = rag_answer(question, langsmith_extra={"run_id": run_id})
    print(f"Answer: {answer}")

    # In a real app, this would be a user clicking thumbs up/down in
    # your UI, sent back to LangSmith as feedback on the run they just
    # saw the output of. create_feedback attaches a score to a run after
    # the fact, the run doesn't need to still be executing.
    client.create_feedback(
        run_id=run_id,
        key="user_thumbs_up",
        score=1,
        comment="Simulated user feedback: this answer looked correct.",
    )

    # An LLM-as-judge score, computed after the fact by a second model
    # call, then published as feedback on the *original* run, the same
    # mechanism as the simulated user feedback above, just a different
    # source for the score.
    helpfulness = judge_helpfulness(question, answer)
    client.create_feedback(
        run_id=run_id,
        key="llm_judged_helpfulness",
        score=helpfulness,
    )
    print(f"Published feedback: user_thumbs_up=1, llm_judged_helpfulness={helpfulness}")


if __name__ == "__main__":
    main()
