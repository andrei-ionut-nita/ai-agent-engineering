"""
Lesson 18: querying runs with filters, and building a small dashboard.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langsmith/03_advanced/18_filtering_and_dashboards/lesson.py

Run Lesson 17 (or any earlier lesson tagging runs "langsmith-course")
at least once first, so there's something in your project for this
lesson to actually find and filter.
"""

import os
from collections import Counter

from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

client = Client()

# The project runs are traced into, LANGSMITH_PROJECT in .env if set,
# otherwise the same "default" project every earlier lesson has been
# writing to.
PROJECT_NAME = os.environ.get("LANGSMITH_PROJECT", "default")


def main() -> None:
    # list_runs accepts a small filter query language: eq/gt/lt/has, and
    # and()/or() to combine them. This pulls every run of type "chain"
    # from the project, most recent first.
    chain_runs = list(
        client.list_runs(
            project_name=PROJECT_NAME,
            run_type="chain",
            limit=50,
        )
    )
    print(f"Found {len(chain_runs)} chain runs.")

    # A run object carries enough fields (name, latency, error, tags) to
    # build simple aggregates locally, exactly what a dashboard panel in
    # the UI does, just computed here in Python instead.
    by_name = Counter(run.name for run in chain_runs)
    print("\nRuns per function name:")
    for name, count in by_name.most_common():
        print(f"  {name}: {count}")

    latencies = [
        (run.end_time - run.start_time).total_seconds()
        for run in chain_runs
        if run.end_time is not None
    ]
    if latencies:
        average_latency = sum(latencies) / len(latencies)
        print(f"\nAverage latency across these runs: {average_latency:.2f}s")

    error_count = sum(1 for run in chain_runs if run.error is not None)
    print(f"Runs with an error: {error_count}/{len(chain_runs)}")

    # Filtering to just the runs this course tagged, a much narrower,
    # more useful slice than "every chain run ever".
    course_runs = list(
        client.list_runs(
            project_name=PROJECT_NAME,
            filter='has(tags, "langsmith-course")',
            limit=50,
        )
    )
    print(f"\nRuns tagged 'langsmith-course': {len(course_runs)}")


if __name__ == "__main__":
    main()
