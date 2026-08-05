"""
Lesson 7: ToolNode + tools_condition, the think/act loop built by hand.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/01_beginner/07_tool_node/lesson.py

New here: a model that can request a tool call, a ToolNode that runs it,
and a conditional edge (tools_condition) that loops back to the model
until it's ready to answer without a tool. This is one tool and a
couple of rounds, deliberately kept small; Lesson 23 (this course's
advanced tier) builds the fully general version from scratch.
"""

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()


@tool
def get_word_length(word: str) -> int:
    """Return the number of characters in a word."""
    return len(word)


model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

# bind_tools makes the model aware it's allowed to request this tool
# instead of answering directly, same as in the langchain course.
model_with_tools = model.bind_tools([get_word_length])


def call_model(state: MessagesState) -> dict:
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}


# ToolNode reads the latest AIMessage's tool_calls, actually runs the
# matching function(s), and returns ToolMessage results. Default node
# name is "tools" unless you pass name=... to override it.
tool_node = ToolNode(tools=[get_word_length])

builder = StateGraph(MessagesState)
builder.add_node("call_model", call_model)
builder.add_node("tools", tool_node)
builder.add_edge(START, "call_model")

# tools_condition returns "tools" if the last message has pending tool
# calls, otherwise "__end__". Saves us writing that check by hand.
builder.add_conditional_edges("call_model", tools_condition)

# After the tool runs, go back to call_model so it can see the result.
# This is the loop: call_model -> tools -> call_model -> ... until
# tools_condition decides no more tool calls are pending.
builder.add_edge("tools", "call_model")

app = builder.compile()


def main() -> None:
    result = app.invoke(
        {"messages": [HumanMessage("How many characters are in the word 'graph'?")]}
    )

    for message in result["messages"]:
        role = message.__class__.__name__
        text = message.text if message.text else "(no text, only a tool call)"
        print(f"{role}: {text}")


if __name__ == "__main__":
    main()
