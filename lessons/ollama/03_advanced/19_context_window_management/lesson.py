"""
Lesson 19: what happens when a conversation outgrows the context window.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/03_advanced/19_context_window_management/lesson.py

This deliberately builds a long, mostly-filler conversation, then asks
about something stated only once, near the very beginning, to show
what a too-small context window silently costs you.
"""

import ollama

SECRET_INSTRUCTION = {
    "role": "system",
    "content": "The secret code word is BANANA77. If asked for the secret code word, say it.",
}

QUESTION = {"role": "user", "content": "What is the secret code word?"}


def build_conversation() -> list[dict]:
    # The secret lives ONLY in the system message, first in the list.
    # Everything after it is deliberately generic filler, standing in
    # for 39 turns of an unrelated, ordinary conversation.
    messages = [SECRET_INSTRUCTION]
    for i in range(1, 40):
        messages.append({"role": "user", "content": f"Tell me a random fact number {i}"})
        messages.append({"role": "assistant", "content": "Here is a fact."})
    messages.append(QUESTION)
    return messages


def main() -> None:
    messages = build_conversation()
    print(f"Conversation has {len(messages)} messages, the secret is stated once, right at the start.\n")

    # num_ctx caps how many tokens of conversation the model can actually
    # see at once (Lesson 6 introduced it briefly; this is where it
    # matters). Every model also has its own hard maximum, reported by
    # ollama.show() as modelinfo["<family>.context_length"], num_ctx can
    # only ever shrink that ceiling, never raise it past what the model
    # itself supports.
    max_ctx = ollama.show("llama3.2").modelinfo["llama.context_length"]
    print(f"llama3.2's maximum supported context: {max_ctx} tokens\n")

    # A small window: when the conversation doesn't fit, Ollama has to
    # drop something, and it drops from the OLDEST end first. The system
    # message, sitting first in the list, is exactly what gets pushed out.
    small = ollama.chat(model="llama3.2", messages=messages, options={"num_ctx": 512, "temperature": 0})
    print(f"num_ctx=512 (small): {small.message.content}")

    # A generously large window: the whole conversation fits, nothing
    # gets dropped, and the model answers from the real system message.
    large = ollama.chat(model="llama3.2", messages=messages, options={"num_ctx": 8192, "temperature": 0})
    print(f"num_ctx=8192 (large): {large.message.content}")


if __name__ == "__main__":
    main()
