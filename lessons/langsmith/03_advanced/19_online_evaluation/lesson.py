"""
Lesson 19: scoring a sample of production runs after the fact.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langsmith/03_advanced/19_online_evaluation/lesson.py

Run a few earlier lessons first (Lesson 3, 6, 7, or 17 all produce
"chain" runs), so there's production-like traffic for this one to find
and score.
"""

import os
import random

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import Client

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
client = Client()

PROJECT_NAME = os.environ.get("LANGSMITH_PROJECT", "default")


def judge_run(question: str, answer: str) -> float:
    verdict = model.invoke(
        f"Question or input: {question}\nAnswer or output: {answer}\n\n"
        f"Reply with exactly one word, yes or no: does the answer look "
        f"like a reasonable, on-topic response?"
    )
    return 1.0 if "yes" in verdict.text.strip().lower() else 0.0


def main() -> None:
    # Pulls recent, already-finished chain runs, the same query style
    # as Lesson 18. A real online evaluation rule runs this same shape
    # of logic continuously and automatically, server-side, on a
    # sample of live traffic, configured from the UI's Rules tab rather
    # than a script you have to remember to re-run.
    recent_runs = list(
        client.list_runs(
            project_name=PROJECT_NAME,
            run_type="chain",
            limit=20,
        )
    )

    # Scoring every run in production would be expensive at real scale,
    # so online evaluation typically samples a fraction of traffic
    # instead of grading everything. 30% here stands in for that.
    sample = [run for run in recent_runs if random.random() < 0.3]
    print(f"Sampling {len(sample)} of {len(recent_runs)} recent runs.")

    for run in sample:
        question = str(run.inputs)[:200]
        answer = str(run.outputs)[:200] if run.outputs else ""
        if not answer:
            continue
        score = judge_run(question, answer)
        client.create_feedback(
            run_id=run.id,
            key="online_eval_reasonable",
            score=score,
            feedback_source_type="model",
        )
        print(f"  {run.name}: online_eval_reasonable={score}")


if __name__ == "__main__":
    main()
