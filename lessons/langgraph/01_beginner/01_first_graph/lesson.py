"""
Lesson 1: a graph with one node, purely mechanical, no AI involved.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/01_beginner/01_first_graph/lesson.py

This lesson does NOT call any model, that starts in Lesson 6. The goal
here is just the shape of a graph: state, a node, edges, compile,
invoke. Everything else in this course builds on these five pieces.
"""

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


# The state schema: a plain dictionary shape with one known key. LangGraph
# uses this to validate what nodes are allowed to read and return.
class GraphState(TypedDict):
    text: str


def shout(state: GraphState) -> dict:
    # A node reads whatever fields it needs off `state` and returns a
    # dictionary of the fields it wants to change. It does NOT return a
    # full new state object, just the part it's updating.
    return {"text": state["text"].upper()}


# Build the graph: register the node, then wire START -> shout -> END.
builder = StateGraph(GraphState)
builder.add_node("shout", shout)
builder.add_edge(START, "shout")
builder.add_edge("shout", END)

# Compile turns the wiring into something runnable. Do this once, then
# invoke the result as many times as you like.
app = builder.compile()


def main() -> None:
    result = app.invoke({"text": "hello graph"})

    # The result is the final state dictionary, same shape as GraphState,
    # after every node on the path from START to END has run.
    print("Input:  hello graph")
    print("Output:", result["text"])


if __name__ == "__main__":
    main()
