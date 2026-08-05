"""
Lesson 34: combining a durable checkpointer and a long-term store.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/03_advanced/34_deploying_persistent_agent/lesson.py

This is what a real deployed agent typically needs: BOTH kinds of memory
at once. SqliteSaver (Lesson 14) gives per-thread memory that survives a
restart. InMemoryStore (Lesson 25) gives cross-thread memory keyed by
something more durable than a thread, like a user id. Neither replaces
the other, they solve different problems, and a compiled graph can hold
both at the same time.
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.store.memory import InMemoryStore

load_dotenv()

DB_PATH = Path(__file__).parent / "checkpoints.sqlite"

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

# The store is shared across every thread, this is the LONG-TERM,
# cross-thread half of memory (Lesson 25). It's created once here, kept
# in RAM for this run; nothing about it changes based on which SqliteSaver
# connection is active.
store = InMemoryStore()


def build_app_for_user(user_id: str, checkpointer):
    def remember(state: MessagesState) -> dict:
        last_text = state["messages"][-1].content
        if "remember" in last_text.lower():
            store.put(("profile", user_id), "note", {"text": last_text})
        return {}

    def chatbot(state: MessagesState) -> dict:
        saved = store.search(("profile", user_id))
        context = "\n".join(item.value["text"] for item in saved)
        note = HumanMessage(f"(Known long-term facts: {context})" if context else "(No known facts.)")
        response = model.invoke([note, *state["messages"]])
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("remember", remember)
    builder.add_node("chatbot", chatbot)
    builder.add_edge(START, "remember")
    builder.add_edge("remember", "chatbot")
    builder.add_edge("chatbot", END)
    # Both memory systems attached to the same compiled graph: a
    # PER-THREAD checkpointer (this conversation's turn-by-turn history,
    # durable across restarts) AND a CROSS-THREAD store (facts that
    # follow the user regardless of which thread they're chatting in).
    return builder.compile(checkpointer=checkpointer, store=store)


def main() -> None:
    user_id = "user-77"

    with SqliteSaver.from_conn_string(str(DB_PATH)) as checkpointer:
        app = build_app_for_user(user_id, checkpointer)

        # Thread 1: per-thread memory (checkpointer) handles the
        # back-and-forth within this one conversation.
        config_1 = {"configurable": {"thread_id": "support-session-1"}}
        r1 = app.invoke({"messages": [HumanMessage("Please remember my account tier is Enterprise.")]}, config_1)
        print("Session 1, turn 1:", r1["messages"][-1].text)

        r2 = app.invoke({"messages": [HumanMessage("What did I just tell you?")]}, config_1)
        print("Session 1, turn 2:", r2["messages"][-1].text)

        # Thread 2: a brand new thread_id, no checkpointer history in
        # common with thread 1 at all. The long-term store still knows
        # the account tier, because that lookup is keyed by user_id, not
        # thread_id, exactly like Lesson 25.
        config_2 = {"configurable": {"thread_id": "support-session-2"}}
        r3 = app.invoke({"messages": [HumanMessage("What account tier am I on?")]}, config_2)
        print("Session 2 (new thread, same user):", r3["messages"][-1].text)

    print(f"\nCheckpoints on disk at: {DB_PATH}")
    print("Run this script again: the checkpointer's thread history persists,")
    print("but the store's facts are in-memory only here, they'd need their own")
    print("persistent backend (a real deployment could use a database-backed store).")


if __name__ == "__main__":
    main()
