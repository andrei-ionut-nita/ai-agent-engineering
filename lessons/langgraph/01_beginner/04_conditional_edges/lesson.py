"""
Lesson 4: add_conditional_edges, routing to a different node at runtime.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/01_beginner/04_conditional_edges/lesson.py

New here: a routing function that inspects state and returns the name
of the next node, instead of every node having exactly one fixed
successor. Lesson 5 takes this further by routing back to an earlier
node, forming a loop.
"""

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class GraphState(TypedDict):
    text: str
    note: str


def clean_text(state: GraphState) -> dict:
    return {"text": state["text"].strip()}


def expand(state: GraphState) -> dict:
    # Runs when the cleaned text is short.
    return {"note": "expanded: this text was short, consider adding detail"}


def truncate(state: GraphState) -> dict:
    # Runs when the cleaned text is long.
    return {"text": state["text"][:20] + "...", "note": "truncated: this text was long"}


def route_by_length(state: GraphState) -> str:
    # A routing function returns a node NAME (a string), not a state
    # update. It reads state but never modifies it.
    if len(state["text"]) <= 20:
        return "expand"
    return "truncate"


builder = StateGraph(GraphState)
builder.add_node("clean_text", clean_text)
builder.add_node("expand", expand)
builder.add_node("truncate", truncate)
builder.add_edge(START, "clean_text")

# After clean_text, call route_by_length with the current state. Its
# return value ("expand" or "truncate") picks the next node.
builder.add_conditional_edges("clean_text", route_by_length)

# Every branch still needs its own path onward.
builder.add_edge("expand", END)
builder.add_edge("truncate", END)

app = builder.compile()


def main() -> None:
    short_result = app.invoke({"text": "hi there", "note": ""})
    print("Short input ->", short_result["note"])

    long_result = app.invoke(
        {"text": "this sentence is definitely longer than twenty characters", "note": ""}
    )
    print("Long input  ->", long_result["note"])
    print("Long input text now:", long_result["text"])


if __name__ == "__main__":
    main()
