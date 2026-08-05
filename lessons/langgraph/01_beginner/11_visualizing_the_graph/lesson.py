"""
Lesson 11: printing the shape of a compiled graph.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/01_beginner/11_visualizing_the_graph/lesson.py

New here: app.get_graph().draw_mermaid(), which prints the compiled
graph's actual structure as text you can cross-check against the
add_node/add_edge calls that built it. We reuse Lesson 7's think/act
loop because it has both a branch and a cycle, the two shapes hardest
to picture from code alone. draw_mermaid_png() is mentioned as an
optional alternative that needs more setup.
"""

from dotenv import load_dotenv
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
model_with_tools = model.bind_tools([get_word_length])


def call_model(state: MessagesState) -> dict:
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}


# Same think/act loop shape as Lesson 7: a branch (call_model -> tools
# or END) and a cycle (tools -> call_model). Good shape to visualize
# because you can't picture it from a single straight read-through.
builder = StateGraph(MessagesState)
builder.add_node("call_model", call_model)
builder.add_node("tools", ToolNode(tools=[get_word_length]))
builder.add_edge(START, "call_model")
builder.add_conditional_edges("call_model", tools_condition)
builder.add_edge("tools", "call_model")

app = builder.compile()


def main() -> None:
    # Mermaid source text, no extra dependencies needed. Paste this into
    # any Mermaid renderer (GitHub renders ```mermaid fences directly)
    # to see the actual picture.
    print(app.get_graph().draw_mermaid())

    # Optional aside: an actual PNG image, needs extra rendering
    # dependencies, not guaranteed to work in every environment.
    # png_bytes = app.get_graph().draw_mermaid_png()
    # with open("graph.png", "wb") as f:
    #     f.write(png_bytes)


if __name__ == "__main__":
    main()
