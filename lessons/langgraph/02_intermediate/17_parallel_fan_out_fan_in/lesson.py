"""
Lesson 17: fan-out and fan-in, running nodes at the same time.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/02_intermediate/17_parallel_fan_out_fan_in/lesson.py

Every graph so far has run one node at a time, in a strict order. This
lesson adds two nodes that read the same input and run concurrently,
then a third node that only runs once both are done. No Send() yet
(Lesson 18), the branching here is fixed at graph-build time, not
decided dynamically from a list.
"""

import operator
from typing import Annotated

from typing_extensions import TypedDict

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


class AnalysisState(TypedDict):
    text: str
    # Both parallel branches below write into this same field, in the
    # same superstep. Without a reducer, LangGraph would raise an error
    # about two nodes writing the same key at once, it has no way to
    # know whether that should be a merge or a genuine conflict.
    # operator.add tells it: concatenate the lists.
    findings: Annotated[list[str], operator.add]
    combined: str


def summarize(state: AnalysisState) -> dict:
    response = model.invoke(f"Summarize this in one short sentence: {state['text']}")
    return {"findings": [f"Summary: {response.text.strip()}"]}


def extract_keywords(state: AnalysisState) -> dict:
    response = model.invoke(
        f"List 3 keywords from this text, comma separated, nothing else: {state['text']}"
    )
    return {"findings": [f"Keywords: {response.text.strip()}"]}


def combine(state: AnalysisState) -> dict:
    # By the time this node runs, BOTH parallel branches have already
    # finished and both of their findings are already merged into the
    # list, thanks to the reducer. combine() doesn't need to know how
    # many branches fed into it, just that findings is complete.
    return {"combined": "\n".join(state["findings"])}


builder = StateGraph(AnalysisState)
builder.add_node("summarize", summarize)
builder.add_node("extract_keywords", extract_keywords)
builder.add_node("combine", combine)

# Two outgoing edges from START, straight to two different nodes. Nodes
# with no unmet dependencies in the same "superstep" (LangGraph's unit of
# execution) run concurrently, so summarize and extract_keywords fire off
# together instead of waiting on each other.
builder.add_edge(START, "summarize")
builder.add_edge(START, "extract_keywords")

# Both branches feed into the same downstream node. combine only runs
# once EVERY edge pointing into it is satisfied, i.e. after both
# summarize and extract_keywords have completed.
builder.add_edge("summarize", "combine")
builder.add_edge("extract_keywords", "combine")
builder.add_edge("combine", END)

app = builder.compile()


def main() -> None:
    text = (
        "LangGraph lets you build applications as graphs of nodes and edges, "
        "giving you explicit control over branching, looping, and parallel "
        "execution that higher-level agent frameworks usually hide from you."
    )
    result = app.invoke({"text": text, "findings": [], "combined": ""})

    print("Findings (from two nodes that ran concurrently):")
    for finding in result["findings"]:
        print(" -", finding)
    print("\nCombined:")
    print(result["combined"])


if __name__ == "__main__":
    main()
