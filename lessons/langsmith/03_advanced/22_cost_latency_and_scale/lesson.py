"""
Lesson 22: token usage, latency, and cost, at the scale of many runs.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langsmith/03_advanced/22_cost_latency_and_scale/lesson.py

Run a few earlier lessons first, so there's more than one or two llm
runs in your project for the aggregates below to be meaningful.
"""

import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import Client

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
client = Client()

PROJECT_NAME = os.environ.get("LANGSMITH_PROJECT", "default")


def main() -> None:
    # A single call, inspected immediately: response.usage_metadata is
    # where LangChain surfaces token counts for the call you just made,
    # the same numbers LangSmith records on that call's "llm" run.
    response = model.invoke("In one sentence, why does token usage matter?")
    usage = response.usage_metadata
    print(f"This call: {usage['input_tokens']} in, {usage['output_tokens']} out, "
          f"{usage['total_tokens']} total tokens.")

    # Beyond a single call, the same numbers are queryable across every
    # past "llm" run in the project, so cost and latency can be tracked
    # in aggregate, not just call by call.
    llm_runs = list(
        client.list_runs(
            project_name=PROJECT_NAME,
            run_type="llm",
            limit=50,
        )
    )
    print(f"\nInspecting {len(llm_runs)} recent llm runs:")

    total_tokens = sum(run.total_tokens or 0 for run in llm_runs)
    total_cost = sum(run.total_cost or 0 for run in llm_runs)
    latencies = [
        (run.end_time - run.start_time).total_seconds()
        for run in llm_runs
        if run.end_time is not None
    ]

    print(f"  Total tokens across these runs: {total_tokens}")
    print(f"  Total cost across these runs: ${total_cost:.6f}")
    if latencies:
        print(f"  Average latency: {sum(latencies) / len(latencies):.2f}s")
        print(f"  Slowest run: {max(latencies):.2f}s")


if __name__ == "__main__":
    main()
