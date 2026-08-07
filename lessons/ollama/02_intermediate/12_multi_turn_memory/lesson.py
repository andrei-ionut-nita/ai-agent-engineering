"""
Lesson 12: real conversation memory, across multiple turns.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/02_intermediate/12_multi_turn_memory/lesson.py

Lesson 9's checkpoint answered each question independently, a fresh
messages list every time. This lesson keeps ONE growing messages list
across turns, so the model can actually refer back to what was said
earlier, exactly like message history in the langchain course.
"""

import ollama

MODEL = "llama3.2"


def main() -> None:
    # One list, reused and appended to across the whole conversation.
    # Ollama (like every model provider) is stateless between calls: it
    # doesn't remember anything on its own. "Memory" is really just you
    # resending the whole conversation so far, every single time.
    messages: list[dict] = []

    def turn(user_text: str) -> None:
        messages.append({"role": "user", "content": user_text})
        response = ollama.chat(model=MODEL, messages=messages, options={"temperature": 0})
        # The model's own reply is appended too, so the NEXT call sees
        # its own earlier answer as part of the history, not just yours.
        messages.append({"role": "assistant", "content": response.message.content})
        print(f"You: {user_text}")
        print(f"Assistant: {response.message.content}\n")

    turn("My favorite color is teal. Remember that.")
    turn("What is my favorite color?")

    print(f"Full conversation so far has {len(messages)} messages.")
    for message in messages:
        print(f"  [{message['role']}] {message['content'][:60]}")


if __name__ == "__main__":
    main()
