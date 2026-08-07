"""
Lesson 22: waiting for Ollama's background service to actually be ready.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/03_advanced/22_running_as_a_background_service/lesson.py

This lesson's real code is small on purpose: the interesting part is
in the README, about how `ollama serve` runs as a background service
on each platform. What IS worth real code is a pattern every program
depending on a background service should have: don't assume it's
ready, wait for it, with a real timeout.
"""

import time

import ollama


def wait_for_ollama(timeout_seconds: float = 10.0, poll_interval: float = 0.5) -> int:
    """Poll the local Ollama server until it responds, or give up.

    Returns the number of attempts it took. Raises TimeoutError if the
    server never became reachable within timeout_seconds.
    """
    deadline = time.time() + timeout_seconds
    attempts = 0

    while time.time() < deadline:
        attempts += 1
        try:
            # ollama.list() is a cheap, side-effect-free call, a good
            # choice for a readiness check: it either succeeds (the
            # server is up) or raises ConnectionError (it isn't yet).
            ollama.list()
            return attempts
        except ConnectionError:
            time.sleep(poll_interval)

    raise TimeoutError(
        f"Ollama did not become reachable within {timeout_seconds}s. "
        "Is the background service running? See this course's README."
    )


def main() -> None:
    print("Waiting for Ollama to be ready...")
    attempts = wait_for_ollama()
    print(f"Ready after {attempts} attempt(s).")

    # Only now, once readiness is confirmed, does the real work start.
    # A program that skips this step and just calls ollama.chat()
    # immediately on startup will crash with a confusing ConnectionError
    # any time it starts before the background service has finished
    # coming up, a real race condition on system boot or container start.
    response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": "Say hello in one word."}])
    print(f"First real call succeeded: {response.message.content}")


if __name__ == "__main__":
    main()
