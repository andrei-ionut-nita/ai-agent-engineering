"""
Lesson 14: SqliteSaver, memory that survives a restart.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/02_intermediate/14_persistent_checkpointer/lesson.py

Lesson 13's InMemorySaver loses everything the moment the program exits,
because it only ever lived in this process's RAM. This lesson swaps it
for SqliteSaver, backed by a real .sqlite file in this lesson's folder.
Run this script twice in a row (or any time later) and turn 2 still
remembers turn 1 from the PREVIOUS run, because the checkpoints live on
disk, not in memory.
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, MessagesState, StateGraph

load_dotenv()

# A real file, sitting next to this script, not a temp path. Deliberately
# NOT deleted at the end of this script, run it twice and see for
# yourself that memory survives between separate `python` invocations.
DB_PATH = Path(__file__).parent / "checkpoints.sqlite"

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


def chatbot(state: MessagesState) -> dict:
    response = model.invoke(state["messages"])
    return {"messages": [response]}


def build_app(checkpointer):
    # Same graph shape as Lesson 13, the only thing that changes between
    # lessons is which checkpointer object gets passed to compile().
    builder = StateGraph(MessagesState)
    builder.add_node("chatbot", chatbot)
    builder.add_edge(START, "chatbot")
    builder.add_edge("chatbot", END)
    return builder.compile(checkpointer=checkpointer)


def main() -> None:
    config = {"configurable": {"thread_id": "persistent-demo"}}

    # SqliteSaver.from_conn_string() opens a connection to a real file on
    # disk and hands it back as a context manager, same pattern as the
    # langchain course's Lesson 32, just wired into our own StateGraph
    # instead of create_agent.
    with SqliteSaver.from_conn_string(str(DB_PATH)) as checkpointer:
        app = build_app(checkpointer)

        result1 = app.invoke(
            {"messages": [HumanMessage("Remember this: my dog's name is Biscuit.")]},
            config,
        )
        print("Turn 1:", result1["messages"][-1].text)

        result2 = app.invoke(
            {"messages": [HumanMessage("What is my dog's name?")]}, config
        )
        print("Turn 2:", result2["messages"][-1].text)

    print(f"\nCheckpoints saved in: {DB_PATH}")
    print(f"File size: {DB_PATH.stat().st_size} bytes")
    print(
        "Run this script again: turn 2 will still know the dog's name, "
        "even though this is a brand new process."
    )


if __name__ == "__main__":
    main()
