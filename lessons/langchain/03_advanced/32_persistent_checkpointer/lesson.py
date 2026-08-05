"""
Lesson 32: a persistent checkpointer, memory that survives a restart.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/03_advanced/32_persistent_checkpointer/lesson.py

Lesson 24's InMemorySaver loses everything when the program exits, the
same real limitation Lesson 17 flagged for a plain Python list. This
lesson swaps it for SqliteSaver, backed by a real file on disk.
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

DB_PATH = Path(__file__).parent / "memory.db"
model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
config = {"configurable": {"thread_id": "persistent-demo"}}


def session_one() -> None:
    """Simulates a program run: tell the agent something, then exit."""
    # SqliteSaver.from_conn_string() opens a connection to a real .db
    # file on disk, same idea as InMemorySaver, but everything gets
    # written to memory.db instead of staying only inside this Python
    # process.
    with SqliteSaver.from_conn_string(str(DB_PATH)) as checkpointer:
        agent = create_agent(model=model, checkpointer=checkpointer)
        result = agent.invoke(
            {"messages": [HumanMessage("My favorite programming language is Python.")]},
            config,
        )
        print("Session 1:", result["messages"][-1].text)
    # The `with` block ending here closes the connection, standing in
    # for the program actually exiting. Nothing about this agent or its
    # memory still exists in this process after this line.


def session_two() -> None:
    """Simulates a SEPARATE, later program run: a brand new agent
    object, a brand new connection, same thread_id, same .db file."""
    with SqliteSaver.from_conn_string(str(DB_PATH)) as checkpointer:
        # A completely new create_agent call. Nothing is shared with
        # session_one() except the thread_id and the .db file on disk.
        agent = create_agent(model=model, checkpointer=checkpointer)
        result = agent.invoke(
            {"messages": [HumanMessage("What is my favorite programming language?")]},
            config,
        )
        print("Session 2:", result["messages"][-1].text)


def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()  # start fresh each time this lesson is run

    session_one()
    session_two()

    print(f"\nMemory persisted in: {DB_PATH}")
    print(f"File size: {DB_PATH.stat().st_size} bytes")


if __name__ == "__main__":
    main()
