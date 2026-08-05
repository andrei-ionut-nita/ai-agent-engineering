"""
Lesson 26: conversation summarization, compressing instead of dropping.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/03_advanced/26_conversation_summarization/lesson.py

Lesson 25's trim_messages solved the context window problem by dropping
old messages entirely, permanently forgetting them. This lesson keeps
old information around, in compressed form, instead of losing it.
"""

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

# Same long, synthetic conversation as Lesson 25.
long_history = [
    HumanMessage("My dog's name is Baxter."),
    AIMessage("Got it, Baxter!"),
    HumanMessage("My favorite food is lasagna."),
    AIMessage("Noted, lasagna is a great choice."),
    HumanMessage("I'm learning to play the violin."),
    AIMessage("That's wonderful, the violin is a beautiful instrument."),
]

# These, on the other hand, are recent enough to keep in full, no
# summarizing needed yet.
recent_messages = [
    HumanMessage("I live in a small town near the coast."),
    AIMessage("Sounds like a lovely place to live."),
    HumanMessage("My favorite color is teal."),
    AIMessage("Teal is a great color."),
]


def summarize(messages: list) -> str:
    # A separate, one-off call: not chatting, just asking the model to
    # compress a chunk of conversation into a short paragraph of facts.
    transcript = "\n".join(f"{m.type}: {m.text}" for m in messages)
    summary_request = [
        HumanMessage(
            "Summarize the key facts from this conversation in one short "
            f"paragraph, keep every specific detail:\n\n{transcript}"
        )
    ]
    return model.invoke(summary_request).text


def main() -> None:
    # Instead of dropping long_history the way Lesson 25's trim_messages
    # did, we compress it into one SystemMessage. This costs one extra
    # model call (the summarization itself), but the information it
    # produces gets kept, not discarded.
    summary_text = summarize(long_history)
    print("Generated summary of the old messages:")
    print(" ", summary_text, "\n")

    # The new, much shorter working history: one summary message,
    # standing in for six original messages, plus the untouched recent
    # ones.
    compressed_history = [
        SystemMessage(f"Summary of earlier conversation: {summary_text}")
    ] + recent_messages

    print(f"Original history: {len(long_history) + len(recent_messages)} messages")
    print(f"Compressed history: {len(compressed_history)} messages\n")

    # Ask about something from the summarized (old) part. Unlike Lesson
    # 25's trimming, this information wasn't dropped, it's compressed
    # into the summary, so it should still be answerable.
    old_question = compressed_history + [HumanMessage("What is my dog's name?")]
    old_answer = model.invoke(old_question)
    print("Asking about something OLD (preserved via summary):")
    print(" ", old_answer.text)


if __name__ == "__main__":
    main()
