"""
Lesson 21: retries and rate limits, handling transient failures gracefully.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/02_intermediate/21_retries_and_rate_limits/lesson.py

This lesson is motivated by something that actually happened while
building this course: real 429 (rate limit) and transient 503 (server
overloaded) errors from the live API. Unlike Lesson 16 (a tool call that
is simply wrong, like dividing by zero), these errors are TRANSIENT,
trying again, after a short wait, often just works.
"""

import time

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def flaky_operation(attempt_counter: list) -> str:
    """A fake operation that fails the first two times it's called, then
    succeeds. Standing in for a real transient failure (like a 429 or a
    503), without needing to actually exhaust a real API quota to
    demonstrate one."""
    attempt_counter[0] += 1
    if attempt_counter[0] < 3:
        raise ConnectionError(f"Simulated transient failure (attempt {attempt_counter[0]})")
    return "Success!"


def retry_with_backoff(func, *args, max_attempts: int = 5) -> str:
    """Try func(*args), and if it raises, wait a bit and try again, up
    to max_attempts times. The wait time DOUBLES after each failure,
    this is called exponential backoff, and it matters because
    hammering a server that's already overloaded with instant retries
    tends to make things worse, not better."""
    wait_seconds = 0.5
    for attempt in range(1, max_attempts + 1):
        try:
            return func(*args)
        except Exception as error:
            if attempt == max_attempts:
                raise
            print(
                f"  Attempt {attempt} failed ({error}), "
                f"waiting {wait_seconds}s before retrying..."
            )
            time.sleep(wait_seconds)
            wait_seconds *= 2


def main() -> None:
    print("Manual retry loop, against a simulated flaky operation:")
    attempt_counter = [0]
    result = retry_with_backoff(flaky_operation, attempt_counter)
    print(f"  Final result: {result}\n")

    # LangChain's chat models already have retry logic like this BUILT
    # IN. max_retries controls how many times it will automatically
    # retry a failed request (like a transient 429 or 503) before
    # giving up and raising the error to your code. You've actually seen
    # this exact mechanism already, every full error traceback from a
    # real API failure earlier included a library called "tenacity",
    # that's what's implementing these automatic retries underneath.
    model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", max_retries=3)
    print(f"This model will automatically retry up to {model.max_retries} times")
    print("on transient errors, before you'd ever see one yourself.")

    response = model.invoke("Say OK.")
    print("\nA normal call still works the same as always:", response.text)


if __name__ == "__main__":
    main()
