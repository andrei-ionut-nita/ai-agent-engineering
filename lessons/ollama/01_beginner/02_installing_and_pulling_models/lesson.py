"""
Lesson 2: the model library, tags, and inspecting a pulled model.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/01_beginner/02_installing_and_pulling_models/lesson.py

This lesson assumes you've already run, in a terminal:

    ollama pull llama3.2
    ollama pull llama3.2:1b

Pulling itself is a `ollama` CLI command, not something you'd normally
do from Python. What Python code CAN do is ask the local server what a
pulled model actually is: its parameter count, quantization, and the
raw prompt template underneath the friendly chat API you'll use from
Lesson 4 on.
"""

import ollama


def describe(model_name: str) -> None:
    info = ollama.show(model_name)
    print(f"{model_name}:")
    print(f"  family: {info.details.family}")
    print(f"  parameter size: {info.details.parameter_size}")
    print(f"  quantization: {info.details.quantization_level}")


def main() -> None:
    # "llama3.2" and "llama3.2:1b" are two TAGS of the same model family.
    # A tag after the colon pins a specific variant; no tag at all is
    # shorthand for ":latest". Smaller tags (1b = 1 billion parameters)
    # trade quality for speed and disk/RAM footprint.
    print("Comparing two tags of the same model family:\n")
    describe("llama3.2")
    describe("llama3.2:1b")

    # ollama.list() reports actual downloaded size, which is what your
    # disk and RAM budget really care about, separate from parameter count.
    print("\nDisk footprint of each, from ollama.list():")
    for model in ollama.list().models:
        if model.model.startswith("llama3.2"):
            size_gb = model.size / 1_000_000_000
            print(f"  {model.model}: {size_gb:.2f} GB")


if __name__ == "__main__":
    main()
