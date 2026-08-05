"""
Lesson 12: Checkpoint project, a text-processing pipeline graph.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/01_beginner/12_beginner_checkpoint_project/lesson.py

This lesson introduces no new concept. It combines everything from
Lessons 1-11 (state with a reducer, linear nodes, a conditional branch,
a loop, and streaming) into one graph, deliberately staying in pure
Python (no model call) so graph mechanics are what's being exercised.
Lesson 13 (02_intermediate/) is next, adding memory via a checkpointer.
"""

import operator
from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph

TARGET_LENGTH = 40


class GraphState(TypedDict):
    text: str
    classification: str
    # Every node appends one note here. operator.add (Lesson 2) means
    # these notes accumulate across the whole run, including however
    # many times the loop below fires, instead of the last note
    # overwriting the ones before it.
    steps: Annotated[list[str], operator.add]
    result: str


def clean(state: GraphState) -> dict:
    return {"text": state["text"].strip(), "steps": ["cleaned"]}


def classify(state: GraphState) -> dict:
    label = "short" if len(state["text"]) <= TARGET_LENGTH else "long"
    return {"classification": label, "steps": [f"classified as {label}"]}


def route_by_classification(state: GraphState) -> str:
    # Routing function (Lesson 4): state in, node name out, no state
    # changes here.
    if state["classification"] == "short":
        return "expand_transform"
    return "shrink_transform"


def expand_transform(state: GraphState) -> dict:
    # The "short" branch: pad the text out with a note.
    padded = state["text"] + " (expanded for readability)"
    return {"text": padded, "steps": ["expanded"]}


def shrink_transform(state: GraphState) -> dict:
    # The "long" branch: trim a bit off each pass. Kept intentionally
    # small per pass so the loop below usually needs more than one trip
    # around, same idea as Lesson 5's grow-until-long-enough loop, just
    # shrinking instead of growing.
    shorter = state["text"][:-5].strip()
    return {"text": shorter, "steps": ["shrunk one pass"]}


def is_short_enough(state: GraphState) -> str:
    # Cycle (Lesson 5): loops back to shrink_transform until the text
    # fits, then continues on to combine.
    if len(state["text"]) <= TARGET_LENGTH:
        return "combine"
    return "shrink_transform"


def combine(state: GraphState) -> dict:
    final = f"[{state['classification'].upper()}] {state['text']}"
    return {"result": final, "steps": ["combined"]}


builder = StateGraph(GraphState)
builder.add_node("clean", clean)
builder.add_node("classify", classify)
builder.add_node("expand_transform", expand_transform)
builder.add_node("shrink_transform", shrink_transform)
builder.add_node("combine", combine)

builder.add_edge(START, "clean")
builder.add_edge("clean", "classify")
builder.add_conditional_edges("classify", route_by_classification)
builder.add_edge("expand_transform", "combine")
builder.add_conditional_edges("shrink_transform", is_short_enough)
builder.add_edge("combine", END)

app = builder.compile()


def run_and_report(label: str, text: str) -> None:
    print(f"--- {label} ---")
    # stream_mode="updates" (Lesson 8) so we can watch each node's
    # contribution, including every pass through the shrink loop, as
    # it happens instead of only seeing the final result.
    for chunk in app.stream({"text": text, "steps": []}, stream_mode="updates"):
        for node_name, update in chunk.items():
            print(f"  {node_name}: {update}")

    final = app.invoke({"text": text, "steps": []})
    print("Final result:", final["result"])
    print("Full step trail:", final["steps"])
    print()


def main() -> None:
    run_and_report("Short input", "a tiny note")
    run_and_report(
        "Long input",
        "this piece of input text is quite long and will need to be trimmed down repeatedly",
    )


if __name__ == "__main__":
    main()
