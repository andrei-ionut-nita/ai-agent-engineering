"""
Lesson 25: InMemoryStore, memory that outlives a single thread.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/03_advanced/25_long_term_memory_store/lesson.py

Lessons 13-14's checkpointer remembers everything WITHIN one thread_id,
but a brand new thread_id starts with a blank slate. This lesson adds an
InMemoryStore, keyed by something more durable than a thread, a user id,
so a fact saved in one conversation is still there in a completely
different, later conversation.
"""

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.store.memory import InMemoryStore

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

# One store, shared across every thread. Namespaces are tuples, here
# ("memories", user_id), so different users' facts never collide even
# though they share the same store object. We close over this instance
# directly in the node functions below rather than relying on LangGraph's
# store-injection, simpler to read and guaranteed to work.
store = InMemoryStore()


def remember(state: MessagesState, user_id: str) -> dict:
    # A tiny, deliberately naive "does this look like a fact worth
    # keeping" check, just enough to demonstrate writing to the store.
    # Real systems would use the model itself to decide what's worth
    # saving; that's a prompt-engineering problem, not a new mechanism.
    last_text = state["messages"][-1].content
    if "remember" in last_text.lower():
        store.put(("memories", user_id), "preference", {"text": last_text})
    return {}


def chatbot(state: MessagesState, user_id: str) -> dict:
    # Pull anything saved for this user, from ANY thread, and prepend it
    # as context. This is the cross-thread part: nothing about thread_id
    # is involved in this lookup, only user_id.
    saved = store.search(("memories", user_id))
    context = "\n".join(item.value["text"] for item in saved)
    system_note = HumanMessage(
        f"(Known facts about this user: {context})" if context else "(No known facts yet.)"
    )
    response = model.invoke([system_note, *state["messages"]])
    return {"messages": [response]}


def build_app_for_user(user_id: str):
    # Each node is wrapped in a lambda that closes over this specific
    # user_id, so the same node functions above stay reusable across
    # however many users a real application might have.
    builder = StateGraph(MessagesState)
    builder.add_node("remember", lambda state: remember(state, user_id))
    builder.add_node("chatbot", lambda state: chatbot(state, user_id))
    builder.add_edge(START, "remember")
    builder.add_edge("remember", "chatbot")
    builder.add_edge("chatbot", END)
    # No checkpointer here on purpose, this lesson isolates the STORE.
    # Lesson 34 combines a checkpointer and a store together.
    return builder.compile()


def main() -> None:
    user_id = "user-42"
    app = build_app_for_user(user_id)

    # Thread A: the user shares a fact worth remembering long-term.
    config_a = {"configurable": {"thread_id": "thread-a"}}
    result1 = app.invoke(
        {"messages": [HumanMessage("Please remember that I'm allergic to peanuts.")]},
        config_a,
    )
    print("Thread A:", result1["messages"][-1].text)

    # Thread B: a totally different thread_id, no checkpointer memory
    # links it to thread A at all. Yet the store, keyed by user_id, still
    # has the fact, because store lookups don't care about thread_id.
    config_b = {"configurable": {"thread_id": "thread-b"}}
    result2 = app.invoke(
        {"messages": [HumanMessage("What allergy should the caterer know about?")]},
        config_b,
    )
    print("Thread B (different thread, same user):", result2["messages"][-1].text)


if __name__ == "__main__":
    main()
