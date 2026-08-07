"""
Lesson 20: sending several requests to Ollama at once.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/03_advanced/20_concurrent_requests/lesson.py
"""

import concurrent.futures
import time

import ollama


def ask(i: int) -> tuple[int, float, str]:
    start = time.time()
    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": f"Say the number {i} and nothing else."}],
        options={"temperature": 0},
    )
    return i, time.time() - start, response.message.content.strip()


def main() -> None:
    n = 4

    # Sequential: one call fully finishes before the next one starts.
    # Total wall time is roughly the sum of each individual call.
    start = time.time()
    for i in range(n):
        ask(i)
    sequential_total = time.time() - start
    print(f"Sequential: {n} calls in {sequential_total:.2f}s total")

    # Concurrent: all n calls are sent to Ollama's local server at once,
    # from n threads. ollama.chat() is a blocking network call, exactly
    # the kind of work Python threads (not just async) can genuinely
    # overlap, since each thread spends most of its time waiting on the
    # server, not doing CPU work of its own.
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=n) as executor:
        results = list(executor.map(ask, range(n)))
    concurrent_total = time.time() - start
    print(f"Concurrent: {n} calls in {concurrent_total:.2f}s total")

    for i, elapsed, answer in results:
        print(f"  request {i}: {elapsed:.2f}s, answered {answer!r}")


if __name__ == "__main__":
    main()
