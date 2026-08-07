"""
Lesson 9 (Checkpoint): a streaming chatbot with a system prompt, fully offline.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/01_beginner/09_beginner_checkpoint_project/lesson.py

This combines everything from the beginner tier: chat() with a system
message (Lesson 4), streaming (Lesson 5), and a fixed temperature for
steadier answers (Lesson 6). No network call anywhere in this file,
check your network connection off if you want proof.
"""

import ollama

SYSTEM_PROMPT = "You are a concise, friendly local assistant. Answer in two sentences or fewer."

QUESTIONS = [
    "What is Python primarily used for?",
    "Name the largest planet in the solar system.",
    "Give one tip for writing clean code.",
]


def ask(question: str) -> str:
    stream = ollama.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        stream=True,
        # A lower, fixed temperature keeps these short factual answers
        # steady rather than wandering, appropriate for a Q&A assistant
        # rather than a creative one (Lesson 6).
        options={"temperature": 0.3},
    )

    answer = ""
    for chunk in stream:
        print(chunk.message.content, end="", flush=True)
        answer += chunk.message.content
    print()
    return answer


def main() -> None:
    print(f"System prompt: {SYSTEM_PROMPT}\n")

    for question in QUESTIONS:
        print(f"You: {question}")
        print("Assistant: ", end="")
        ask(question)
        print()


if __name__ == "__main__":
    main()
