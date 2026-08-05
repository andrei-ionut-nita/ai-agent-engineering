"""
Lesson 18: Send, fanning out dynamically over a list.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/02_intermediate/18_send_api_map_reduce/lesson.py

Lesson 17's fan-out was fixed when the graph was built: always exactly
two branches, summarize and extract_keywords. This lesson fans out over
a list whose length is only known at runtime, one worker per item, using
Send. This is LangGraph's version of a "map" step, dispatch N independent
jobs, then a "reduce" step gathers all N results.
"""

import operator
from typing import Annotated

from typing_extensions import TypedDict

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


class TopicState(TypedDict):
    topics: list[str]
    facts: Annotated[list[str], operator.add]


# The per-worker state is intentionally its own small dict, not the full
# TopicState. Each Send() call below hands worker() exactly one topic, it
# has no visibility into the other topics or how many there are.
class WorkerState(TypedDict):
    topic: str


def dispatch(state: TopicState):
    # A conditional-edge-style function, but instead of returning a node
    # NAME (like Lesson 4's routing), it returns a LIST of Send objects,
    # one per topic. LangGraph runs one worker() invocation per Send,
    # concurrently, each seeing only that Send's own state dict.
    return [Send("worker", {"topic": topic}) for topic in state["topics"]]


def worker(state: WorkerState) -> dict:
    response = model.invoke(f"State one interesting fact about {state['topic']} in one sentence.")
    # This return value lands in the SHARED TopicState's "facts" field,
    # even though worker() itself only ever saw a single topic. The
    # operator.add reducer is what collects every worker's single-item
    # list into one combined list, same mechanism as Lesson 17.
    return {"facts": [f"{state['topic']}: {response.text.strip()}"]}


def combine(state: TopicState) -> dict:
    return {}


builder = StateGraph(TopicState)
builder.add_node("worker", worker)
builder.add_node("combine", combine)

# add_conditional_edges with a function that returns Send objects: the
# list of possible destination node names ("worker") is still declared
# for graph-visualization purposes, but the actual number of dispatches
# happens at runtime, once state["topics"] is known.
builder.add_conditional_edges(START, dispatch, ["worker"])
builder.add_edge("worker", "combine")
builder.add_edge("combine", END)

app = builder.compile()


def main() -> None:
    topics = ["octopuses", "volcanoes", "the number zero"]
    result = app.invoke({"topics": topics, "facts": []})

    print(f"Dispatched {len(topics)} workers, one per topic:")
    for fact in result["facts"]:
        print(" -", fact)


if __name__ == "__main__":
    main()
