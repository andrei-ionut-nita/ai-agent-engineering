"""
Lesson 2: partial state updates get merged, and reducers control HOW.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/01_beginner/02_state_and_reducers/lesson.py

New here: a second state field, and Annotated[list, operator.add] as a
reducer so that field accumulates across nodes instead of being
overwritten. Still no AI model, still a straight line of nodes (Lesson
3 chains more of these, Lesson 4 adds branching).
"""

import operator
from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class GraphState(TypedDict):
    # Plain field: no Annotated wrapper, so it uses the default
    # last-write-wins behavior, same as Lesson 1's `text`.
    text: str
    # Reduced field: operator.add tells LangGraph to combine each node's
    # returned value with the existing one using `+` (list concatenation),
    # instead of replacing it outright.
    history: Annotated[list[str], operator.add]


def clean(state: GraphState) -> dict:
    # Only returns a single-item list. The reducer is what appends it to
    # whatever history already exists, this node doesn't need to know or
    # care what came before.
    return {"text": state["text"].strip(), "history": ["cleaned"]}


def shout(state: GraphState) -> dict:
    return {"text": state["text"].upper(), "history": ["shouted"]}


builder = StateGraph(GraphState)
builder.add_node("clean", clean)
builder.add_node("shout", shout)
builder.add_edge(START, "clean")
builder.add_edge("clean", "shout")
builder.add_edge("shout", END)

app = builder.compile()


def main() -> None:
    result = app.invoke({"text": "  hello graph  ", "history": []})

    print("Final text:", repr(result["text"]))
    # Both "cleaned" and "shouted" show up here, even though each node
    # only ever returned a single-item list. That's the reducer at work.
    print("History (accumulated):", result["history"])


if __name__ == "__main__":
    main()
