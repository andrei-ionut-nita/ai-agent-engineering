"""
Lesson 5: a cycle, a conditional edge that routes back to an earlier node.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/01_beginner/05_cycles_and_loops/lesson.py

New here: the routing function can send execution back to a node
already visited (here, back to itself), forming a loop. This is
something a straight-line LCEL chain from the langchain course cannot
do. Still no AI model, still no recursion_limit safety net (Lesson 10).
"""

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class GraphState(TypedDict):
    text: str
    target_length: int


def grow(state: GraphState) -> dict:
    # Each pass appends a word. Nothing here knows or cares how many
    # times it's been called, all the looping logic lives in the
    # routing function below.
    return {"text": state["text"] + " more"}


def is_long_enough(state: GraphState) -> str:
    # Returning END is allowed here, same as returning any node's name.
    # It tells LangGraph "stop, don't route anywhere else."
    if len(state["text"]) >= state["target_length"]:
        return END
    # Returning "grow" sends execution back to the node we just ran,
    # this is the cycle: grow -> is_long_enough -> grow -> ...
    return "grow"


builder = StateGraph(GraphState)
builder.add_node("grow", grow)
builder.add_edge(START, "grow")
builder.add_conditional_edges("grow", is_long_enough)

app = builder.compile()


def main() -> None:
    result = app.invoke({"text": "seed", "target_length": 30})

    print("Final text:", repr(result["text"]))
    print("Final length:", len(result["text"]), "(target was 30)")


if __name__ == "__main__":
    main()
