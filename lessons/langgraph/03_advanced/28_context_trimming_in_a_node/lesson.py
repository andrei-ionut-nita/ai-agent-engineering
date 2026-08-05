"""
Lesson 28: trimming messages inside a node before they reach the model.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/03_advanced/28_context_trimming_in_a_node/lesson.py

trim_messages is the same utility the langchain course used at the top
level (langchain course, lesson 25). Here it runs inside a node, right
before the model call, so a graph with a loop (Lesson 5's shape) can run
many iterations without state["messages"] growing without bound in what
actually gets sent to the model.
"""

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, trim_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, MessagesState, StateGraph

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

# Canned questions fed into the loop one at a time, standing in for a
# long-running conversation happening across many iterations of the
# same graph run. The last one deliberately asks about the first fact,
# so the demo shows exactly what trimming costs you.
QUESTIONS = [
    "My name is Alex.",
    "I live in Denver.",
    "My favorite color is teal.",
    "I have a cat named Whiskers.",
    "I work as a chemist.",
    "My favorite food is ramen.",
    "I collect vintage postcards.",
    "What is my name?",
]


def chatbot(state: MessagesState) -> dict:
    # Feed in the next canned question, as if it just arrived, on top of
    # everything accumulated in state["messages"] so far.
    step = len([m for m in state["messages"] if isinstance(m, HumanMessage)])
    next_question = HumanMessage(QUESTIONS[step])

    full_history = [*state["messages"], next_question]

    # Trim BEFORE calling the model. state["messages"] itself is never
    # touched here, we're only shrinking what gets SENT for this one
    # call. max_tokens is deliberately tiny (counting each message as 1
    # "token") so trimming becomes visible after only a few iterations.
    trimmed = trim_messages(
        full_history,
        max_tokens=4,
        token_counter=len,
        strategy="last",
        include_system=False,
    )
    # A short system instruction keeps replies terse and on-topic, so the
    # trimming effect is easy to see instead of getting masked by the
    # model re-stating earlier facts inside its own chatty answers.
    system = SystemMessage("Answer only the latest question, in one short sentence. Do not recap prior facts.")
    response = model.invoke([system, *trimmed])
    return {"messages": [next_question, response]}


def should_continue(state: MessagesState) -> str:
    answered = len([m for m in state["messages"] if isinstance(m, HumanMessage)])
    return "chatbot" if answered < len(QUESTIONS) else END


builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
# Same loop shape as Lesson 5: a conditional edge sends the graph back to
# itself until every question has been asked, accumulating messages in
# state the entire time, even though the model itself only ever sees a
# trimmed slice of them.
builder.add_conditional_edges("chatbot", should_continue)
app = builder.compile()


def main() -> None:
    result = app.invoke({"messages": []})

    for message in result["messages"]:
        role = "You" if isinstance(message, HumanMessage) else "Agent"
        print(f"{role}: {message.text}")

    print(f"\nTotal messages accumulated in state: {len(result['messages'])}")
    print(
        "The model never saw more than the last few of those on any single "
        "call, that's why the final answer above likely doesn't know your name anymore."
    )


if __name__ == "__main__":
    main()
