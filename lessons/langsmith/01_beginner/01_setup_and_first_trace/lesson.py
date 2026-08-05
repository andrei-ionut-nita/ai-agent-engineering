"""
Lesson 1: turn on tracing and record your first run.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langsmith/01_beginner/01_setup_and_first_trace/lesson.py
"""

from dotenv import load_dotenv
from langsmith import traceable

# Reads LANGSMITH_API_KEY and LANGSMITH_TRACING from .env at the project
# root. LangSmith is a separate service from Google/Gemini: this key
# proves who's sending traces, the same way GOOGLE_API_KEY proves who's
# asking Gemini for an answer.
load_dotenv()


# @traceable wraps this plain function so that, every time it's called,
# LangSmith records a "run": the inputs it was given, the output it
# returned, how long it took, and whether it raised an error. None of
# that requires LangChain, @traceable works on any Python function.
@traceable
def summarize(text: str) -> str:
    words = text.split()
    return f"{len(words)} words, starts with: {' '.join(words[:5])}..."


def main() -> None:
    result = summarize(
        "LangSmith records what happens every time a traced function runs,"
        " so you can look at it later instead of guessing."
    )
    print(result)


if __name__ == "__main__":
    main()
