"""
Lesson 2: nested traces, and the run tree they form.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langsmith/01_beginner/02_tracing_basics/lesson.py
"""

from dotenv import load_dotenv
from langsmith import traceable

load_dotenv()


# A @traceable function calling other @traceable functions is the normal
# case, not a special one. LangSmith notices when a traced call happens
# while another traced call is already running, and links the inner one
# as a child of the outer one.
@traceable
def clean(text: str) -> str:
    return text.strip().lower()


@traceable
def count_words(text: str) -> int:
    return len(text.split())


@traceable
def analyze(text: str) -> dict:
    cleaned = clean(text)
    word_count = count_words(cleaned)
    return {"cleaned": cleaned, "word_count": word_count}


def main() -> None:
    result = analyze("  Some Text, With Odd SPACING and Caps  ")
    print(result)


if __name__ == "__main__":
    main()
