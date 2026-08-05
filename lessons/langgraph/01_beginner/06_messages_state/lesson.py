"""
Lesson 6: MessagesState, calling a model from inside a node.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/01_beginner/06_messages_state/lesson.py

New here: the first graph that actually talks to an AI model, and
MessagesState, LangGraph's ready-made state shape for conversations
(a "messages" field using the add_messages reducer, which appends new
messages instead of overwriting the list). Lesson 7 adds a tool this
model can call, Lesson 9 streams its reply token by token.
"""

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.graph import END, START, MessagesState, StateGraph

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


def call_model(state: MessagesState) -> dict:
    # state["messages"] is the full conversation so far. Passing the
    # whole list gives the model complete context, same as passing a
    # list of messages to .invoke() directly in the langchain course.
    response = model.invoke(state["messages"])

    # Return only the new message. add_messages (baked into
    # MessagesState) is responsible for appending it onto the existing
    # list, this node never has to hand back history it didn't create.
    return {"messages": [response]}


builder = StateGraph(MessagesState)
builder.add_node("call_model", call_model)
builder.add_edge(START, "call_model")
builder.add_edge("call_model", END)

app = builder.compile()


def main() -> None:
    result = app.invoke(
        {"messages": [HumanMessage("What is a graph, in one sentence?")]}
    )

    # Both the original question and the model's reply are in here now,
    # add_messages appended the reply onto the list we started with.
    for message in result["messages"]:
        role = message.__class__.__name__
        print(f"{role}: {message.text}")


if __name__ == "__main__":
    main()
