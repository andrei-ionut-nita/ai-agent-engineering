"""
Lesson 5: grouping multi-turn runs into a conversation thread.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langsmith/01_beginner/05_conversational_threads/lesson.py
"""

import uuid

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import traceable

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


# LangSmith has no idea, on its own, that separate calls belong to the
# same conversation. metadata.thread_id is the convention its UI looks
# for to group runs into a single thread view. Tracing a thread and the
# model actually remembering earlier turns are two separate things:
# this function passes the accumulated history in so the model's
# answers are genuinely coherent, thread_id is what makes that
# coherence visible as one thread in the UI rather than unrelated runs.
@traceable
def chat_turn(conversation_id: str, history: list[BaseMessage]) -> str:
    # LangChain's own config dict carries thread_id down into the nested
    # "llm" run it creates for this Gemini call.
    response = model.invoke(
        history,
        config={"metadata": {"thread_id": conversation_id}},
    )
    return response.text


def main() -> None:
    # A fresh id per run of this script, so each run of the lesson forms
    # its own thread instead of all runs merging into one giant thread.
    conversation_id = str(uuid.uuid4())

    turns = [
        "My favorite programming language is Python. Remember that.",
        "What's my favorite programming language?",
    ]
    history: list[BaseMessage] = []
    for message in turns:
        history.append(HumanMessage(message))
        # langsmith_extra is a special kwarg every @traceable function
        # accepts at call time: it attaches metadata to *this specific
        # run* of chat_turn, the same thread_id used inside it above.
        reply = chat_turn(
            conversation_id,
            history,
            langsmith_extra={"metadata": {"thread_id": conversation_id}},
        )
        history.append(("ai", reply))
        print(f"user: {message}")
        print(f"model: {reply}\n")


if __name__ == "__main__":
    main()
