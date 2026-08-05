"""
Lesson 2: message types, System vs Human vs AI messages.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/01_beginner/02_message_types/lesson.py

Lesson 1 sent a bare string to the model. This lesson sends a LIST of
message objects instead, each one labeled with who it's "from". This is
the format everything from here on (templates, tools, memory, agents)
actually builds on top of.
"""

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


def main() -> None:
    # Instead of one bare string, we build a list of labeled messages.
    # SystemMessage: standing instructions for how the AI should behave.
    # HumanMessage: something the user said.
    messages = [
        SystemMessage("You are a pirate. Answer everything in pirate speak."),
        HumanMessage("What is LangChain?"),
    ]

    response = model.invoke(messages)
    print("Response type:", type(response).__name__)
    print("Reply:", response.text)

    # response is actually an AIMessage, the third type. We can add it
    # back into our list, then add a new HumanMessage, and send the
    # WHOLE list again. The model will see the full exchange, not just
    # the newest line, this is a first look at what Lesson 17 will call
    # "memory".
    messages.append(response)
    messages.append(HumanMessage("Say that again, but in one word."))

    second_response = model.invoke(messages)
    print("\nSecond reply:", second_response.text)


if __name__ == "__main__":
    main()
