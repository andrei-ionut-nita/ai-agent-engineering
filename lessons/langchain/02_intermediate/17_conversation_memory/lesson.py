"""
Lesson 17: memory is just resending the conversation so far.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/02_intermediate/17_conversation_memory/lesson.py

Type messages at the prompt. Try telling it your name, then a couple of
messages later, ask it what your name is. Type "quit" to exit.
"""

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


def main() -> None:
    # This list IS the memory. There's no hidden "remember this" feature
    # inside `model`, it's a fresh connection with no memory of its own.
    # Every entry we add here is something we will resend, in full, on
    # every future turn, for as long as this program keeps running.
    history: list[HumanMessage | AIMessage] = []

    print("Chat with the AI. Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            break
        if not user_input:
            continue

        history.append(HumanMessage(user_input))

        # We send the WHOLE history, not just this one message. The model
        # only "remembers" earlier turns because they are physically
        # present, again, in this list, every single time.
        response = model.invoke(history)

        # Keep the AI's own reply in history too, otherwise the next turn
        # would be missing half the conversation, only your side of it.
        history.append(response)

        print(f"AI: {response.text}\n")

    print(f"\n(Conversation had {len(history)} messages when it ended.)")


if __name__ == "__main__":
    main()
