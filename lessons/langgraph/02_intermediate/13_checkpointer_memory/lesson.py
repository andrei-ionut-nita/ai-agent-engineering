"""
Lesson 13: InMemorySaver, giving a graph real memory across calls.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/02_intermediate/13_checkpointer_memory/lesson.py

Every graph so far (Lesson 6's model node included) forgot everything
the moment .invoke() returned, each call started from whatever messages
you handed it, nothing more. This lesson adds a checkpointer, so the
graph remembers earlier turns automatically, without us managing a list
by hand.
"""

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


def chatbot(state: MessagesState) -> dict:
    # Same shape as Lesson 6: read the accumulated messages, call the
    # model on all of them, return the reply so add_messages appends it.
    response = model.invoke(state["messages"])
    return {"messages": [response]}


builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

# compile(checkpointer=...) is the only new line. InMemorySaver saves a
# snapshot of state after every node runs, keyed by thread_id, all inside
# this process's RAM, gone the moment the program exits (Lesson 14 fixes
# that part).
app = builder.compile(checkpointer=InMemorySaver())


def main() -> None:
    # Every call tagged with this thread_id shares remembered state. The
    # checkpointer looks up whatever happened before under this ID and
    # prepends it, before the graph ever sees the new message.
    config_a = {"configurable": {"thread_id": "conversation-a"}}

    result1 = app.invoke(
        {"messages": [HumanMessage("My favorite color is teal.")]}, config_a
    )
    print("Turn 1:", result1["messages"][-1].text)

    # Only the new message is sent, same as create_agent + InMemorySaver
    # in the langchain course. The checkpointer supplies everything
    # earlier under "conversation-a" automatically.
    result2 = app.invoke(
        {"messages": [HumanMessage("What is my favorite color?")]}, config_a
    )
    print("Turn 2:", result2["messages"][-1].text)

    # A different thread_id is a completely separate, unrelated
    # conversation, even though it's the exact same compiled `app`.
    config_b = {"configurable": {"thread_id": "conversation-b"}}
    result3 = app.invoke(
        {"messages": [HumanMessage("What is my favorite color?")]}, config_b
    )
    print("Turn 3 (different thread):", result3["messages"][-1].text)


if __name__ == "__main__":
    main()
