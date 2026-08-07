"""
Lesson 4: ollama.generate() vs ollama.chat(), and why chat wins.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/01_beginner/04_chat_vs_generate/lesson.py
"""

import ollama

PROMPT = "What is a REST API?"


def with_generate() -> str:
    # generate() takes one flat string. To add a system instruction, you'd
    # have to hand-glue it onto the prompt yourself, and the model's chat
    # template (from Lesson 2's ollama.show()) may or may not interpret
    # that gluing the way you intend.
    response = ollama.generate(
        model="llama3.2",
        prompt=f"You are a terse assistant. Answer in one sentence.\n\n{PROMPT}",
    )
    return response.response


def with_chat() -> str:
    # chat() takes a list of role-tagged messages, the same shape as
    # LangChain's messages in this repo's other courses. The model's own
    # chat template (baked in when it was fine-tuned) turns this into the
    # correct underlying prompt format for you, correctly, every time.
    response = ollama.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": "You are a terse assistant. Answer in one sentence."},
            {"role": "user", "content": PROMPT},
        ],
    )
    return response.message.content


def main() -> None:
    print("generate() with a hand-glued system instruction:")
    print(f"  {with_generate()}\n")

    print("chat() with a proper system message:")
    print(f"  {with_chat()}")


if __name__ == "__main__":
    main()
