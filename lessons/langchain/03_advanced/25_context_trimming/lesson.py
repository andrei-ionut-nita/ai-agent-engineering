"""
Lesson 25: context trimming, keeping a long conversation within limits.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/03_advanced/25_context_trimming/lesson.py

Lesson 17 flagged a real limitation: every message ever sent gets resent
on every future turn, and models can only read so much text at once (the
context window). This lesson introduces trim_messages, one way to keep
a long conversation from growing forever.
"""

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, trim_messages
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

# A long, synthetic conversation: five unrelated exchanges, oldest first.
# In a real app, this is what a long chat session's `history` (Lesson
# 17) would look like after many turns.
long_history = [
    SystemMessage("You are a helpful assistant."),
    HumanMessage("My dog's name is Baxter."),
    AIMessage("Got it, Baxter!"),
    HumanMessage("My favorite food is lasagna."),
    AIMessage("Noted, lasagna is a great choice."),
    HumanMessage("I'm learning to play the violin."),
    AIMessage("That's wonderful, the violin is a beautiful instrument."),
    HumanMessage("I live in a small town near the coast."),
    AIMessage("Sounds like a lovely place to live."),
    HumanMessage("My favorite color is teal."),
    AIMessage("Teal is a great color."),
]


def main() -> None:
    # trim_messages cuts a message list down to fit under a token
    # budget. strategy="last" keeps the MOST RECENT messages and drops
    # the oldest ones first, the opposite would be strategy="first".
    # include_system=True makes sure the SystemMessage survives
    # trimming even though it's the very first message chronologically,
    # standing instructions are usually worth keeping no matter what.
    trimmed = trim_messages(
        long_history,
        max_tokens=60,
        token_counter=model,
        strategy="last",
        include_system=True,
    )

    print(f"Original history: {len(long_history)} messages")
    print(f"Trimmed history:  {len(trimmed)} messages\n")

    print("What survived trimming:")
    for message in trimmed:
        print(f"  [{message.type}] {message.content}")

    # Ask about something from the END of the conversation, recent
    # enough to have survived trimming.
    recent_question = trimmed + [HumanMessage("What is my favorite color?")]
    recent_answer = model.invoke(recent_question)
    print("\nAsking about something RECENT (survived trimming):")
    print(" ", recent_answer.text)

    # Ask about something from the START of the conversation, the dog's
    # name, which trimming likely dropped to stay under the token
    # budget. The model can only answer from what's actually still in
    # the list it was given.
    old_question = trimmed + [HumanMessage("What is my dog's name?")]
    old_answer = model.invoke(old_question)
    print("\nAsking about something OLD (likely trimmed away):")
    print(" ", old_answer.text)


if __name__ == "__main__":
    main()
