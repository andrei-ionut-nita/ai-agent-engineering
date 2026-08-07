"""
Lesson 6: options that shape how a model answers: temperature, seed, num_predict.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/01_beginner/06_model_parameters/lesson.py
"""

import ollama


def ask(prompt: str, **options) -> str:
    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": prompt}],
        options=options,
    )
    return response.message.content


def main() -> None:
    # temperature controls randomness: 0.0 makes the model always pick the
    # single most likely next word, so the same prompt (with the same seed)
    # gives the same answer every time. Deterministic, but repetitive if
    # you ask for anything creative.
    print("temperature=0.0, seed=42, asked twice:")
    print(f"  {ask('Name one fruit.', temperature=0.0, seed=42)}")
    print(f"  {ask('Name one fruit.', temperature=0.0, seed=42)}")

    # Higher temperature lets the model occasionally pick less-likely
    # words, which is what makes creative or varied output possible, at
    # the cost of losing that repeatability.
    print("\ntemperature=1.5, a creative prompt:")
    print(f"  {ask('Give a 4-word product tagline for a coffee shop.', temperature=1.5)}")

    # num_predict caps how many tokens the model is allowed to generate,
    # a hard length limit, unrelated to temperature. Useful when you need
    # a short answer and don't want to pay (in time or tokens) for a long
    # one, or when generating structured fields with a known max size.
    print("\nnum_predict=5, an open-ended prompt:")
    print(f"  {ask('Explain the water cycle in detail.', num_predict=5)}")


if __name__ == "__main__":
    main()
