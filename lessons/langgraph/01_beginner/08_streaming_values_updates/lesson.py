"""
Lesson 8: streaming a graph run, stream_mode="values" vs "updates".

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/01_beginner/08_streaming_values_updates/lesson.py

New here: .stream() instead of .invoke(), yielding one chunk per node
instead of waiting for the whole run to finish. "values" chunks are
full state snapshots, "updates" chunks are just the diff each node
produced. Lesson 9 streams model tokens specifically, a different mode.
"""

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class GraphState(TypedDict):
    raw_text: str
    words: list[str]
    word_count: int
    summary: str


def clean_text(state: GraphState) -> dict:
    return {"raw_text": state["raw_text"].strip().lower()}


def split_words(state: GraphState) -> dict:
    return {"words": state["raw_text"].split()}


def count_words(state: GraphState) -> dict:
    return {"word_count": len(state["words"])}


def format_summary(state: GraphState) -> dict:
    return {"summary": f"{state['word_count']} words: {', '.join(state['words'])}"}


# Same four-node pipeline as Lesson 3, unchanged. Only how we run it
# is new in this lesson.
builder = StateGraph(GraphState)
builder.add_node("clean_text", clean_text)
builder.add_node("split_words", split_words)
builder.add_node("count_words", count_words)
builder.add_node("format_summary", format_summary)
builder.add_edge(START, "clean_text")
builder.add_edge("clean_text", "split_words")
builder.add_edge("split_words", "count_words")
builder.add_edge("count_words", "format_summary")
builder.add_edge("format_summary", END)

app = builder.compile()


def main() -> None:
    initial_state = {"raw_text": "  LangGraph Streams Step By Step  "}

    print("=== stream_mode='values' (full state snapshot each step) ===")
    for chunk in app.stream(initial_state, stream_mode="values"):
        print(chunk)

    print()
    print("=== stream_mode='updates' (just the diff each node returned) ===")
    for chunk in app.stream(initial_state, stream_mode="updates"):
        print(chunk)


if __name__ == "__main__":
    main()
