"""
Lesson 7: Beginner Checkpoint - Traced Multi-Step Pipeline.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langsmith/01_beginner/07_beginner_checkpoint_project/lesson.py
"""

import uuid

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import traceable

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


@traceable(run_type="tool", tags=["beginner-checkpoint"])
def clean(text: str) -> str:
    return text.strip()


@traceable(run_type="tool", tags=["beginner-checkpoint"])
def word_count(text: str) -> int:
    return len(text.split())


@traceable(run_type="chain", tags=["beginner-checkpoint"])
def classify_sentiment(text: str, batch_id: str) -> str:
    # The nested Gemini call below is auto-traced as its own "llm" run
    # (Lesson 3), this wrapper is a "chain" run around it.
    response = model.invoke(
        f"Reply with exactly one word, positive, negative, or neutral, "
        f"describing the sentiment of: {text}",
        config={"metadata": {"thread_id": batch_id}},
    )
    return response.text.strip().lower()


@traceable(
    run_type="chain",
    tags=["beginner-checkpoint"],
    metadata={"lesson": 7},
)
def process_review(review: str, batch_id: str) -> dict:
    cleaned = clean(review)
    return {
        "word_count": word_count(cleaned),
        "sentiment": classify_sentiment(cleaned, batch_id),
    }


def main() -> None:
    # One batch_id groups every review processed in this run into a
    # single thread (Lesson 5), so the UI shows them as one session
    # instead of three unrelated top-level runs.
    batch_id = str(uuid.uuid4())

    reviews = [
        "  This product completely changed how I work, love it.  ",
        "Broke after two days. Would not recommend.",
        "It's fine. Does what it says, nothing more.",
    ]

    for review in reviews:
        result = process_review(
            review,
            batch_id,
            langsmith_extra={"metadata": {"thread_id": batch_id}},
        )
        print(f"{result['sentiment']:>8} ({result['word_count']:>2} words): {review.strip()}")


if __name__ == "__main__":
    main()
