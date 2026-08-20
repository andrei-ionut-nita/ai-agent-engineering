"""
Lesson 1: what Langflow is, and proving the local server is alive.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Langflow is running first, in its own
terminal, and leave it running for the rest of this course):

    uv run langflow run --no-open-browser
    uv run python lessons/langflow/01_beginner/01_what_is_langflow/lesson.py
"""

import httpx

LANGFLOW_URL = "http://127.0.0.1:7860"


def main() -> None:
    version = httpx.get(f"{LANGFLOW_URL}/api/v1/version").json()
    health = httpx.get(f"{LANGFLOW_URL}/health_check").json()

    print(f"Langflow {version['version']} is up at {LANGFLOW_URL}")
    print(f"health_check -> {health}")


if __name__ == "__main__":
    main()
