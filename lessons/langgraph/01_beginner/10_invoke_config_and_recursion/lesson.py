"""
Lesson 10: the config dict and recursion_limit, deliberately triggered.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/01_beginner/10_invoke_config_and_recursion/lesson.py

New here: the config dict passed to .invoke()/.stream(), and
recursion_limit specifically, the safety net that stops a cycle
(Lesson 5) from running forever. We reuse Lesson 5's grow-until-long-
enough loop and cap the limit too low on purpose, to see
GraphRecursionError get raised, then run it again with a sane limit.
"""

from typing_extensions import TypedDict

from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, StateGraph


class GraphState(TypedDict):
    text: str
    target_length: int


def grow(state: GraphState) -> dict:
    return {"text": state["text"] + " more"}


def is_long_enough(state: GraphState) -> str:
    if len(state["text"]) >= state["target_length"]:
        return END
    return "grow"


# Same loop as Lesson 5, unchanged.
builder = StateGraph(GraphState)
builder.add_node("grow", grow)
builder.add_edge(START, "grow")
builder.add_conditional_edges("grow", is_long_enough)

app = builder.compile()


def main() -> None:
    initial_state = {"text": "seed", "target_length": 30}

    print("Attempt 1: recursion_limit=3 (too low for this loop to finish)")
    try:
        # recursion_limit lives directly on the config dict, not nested
        # inside "configurable" (that nested key is for thread_id and
        # friends, starting in Lesson 13).
        app.invoke(initial_state, config={"recursion_limit": 3})
    except GraphRecursionError as exc:
        print("  Hit the safety net as expected:", exc)

    print()
    print("Attempt 2: recursion_limit=25 (the default, plenty for this loop)")
    result = app.invoke(initial_state, config={"recursion_limit": 25})
    print("  Succeeded, final text:", repr(result["text"]))


if __name__ == "__main__":
    main()
