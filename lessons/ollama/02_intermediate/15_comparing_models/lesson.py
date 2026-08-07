"""
Lesson 15: comparing models side by side, speed, size, and a load-time trap.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/02_intermediate/15_comparing_models/lesson.py

This lesson assumes you've pulled all three models used below:

    ollama pull llama3.2:1b
    ollama pull llama3.2
    ollama pull llama3
"""

import time

import ollama

MODELS = ["llama3.2:1b", "llama3.2", "llama3"]
PROMPT = "Write a haiku about debugging code."


def timed_chat(model: str) -> tuple[float, int]:
    start = time.time()
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": PROMPT}],
        options={"temperature": 0.7, "seed": 7},
    )
    elapsed = time.time() - start
    return elapsed, response.eval_count


def main() -> None:
    # Only one model can be actively generating on your GPU/CPU at a time.
    # Switching to a DIFFERENT model than whatever was last loaded means
    # Ollama has to swap it into memory first, which can take several
    # seconds, on top of the actual generation time. Calling every model
    # once here "warms up" all three before the real, fair comparison.
    print("Warming up (loading each model into memory once)...")
    for model in MODELS:
        ollama.chat(model=model, messages=[{"role": "user", "content": "hi"}])

    print("\nTimed generation, same prompt, all models already warm:\n")
    for model in MODELS:
        elapsed, tokens = timed_chat(model)
        tokens_per_sec = tokens / elapsed if elapsed > 0 else 0
        print(f"  {model}: {elapsed:.2f}s, {tokens} tokens, {tokens_per_sec:.1f} tok/s")


if __name__ == "__main__":
    main()
