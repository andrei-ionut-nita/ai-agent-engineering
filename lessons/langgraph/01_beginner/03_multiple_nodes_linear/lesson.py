"""
Lesson 3: four nodes chained in a straight line, no branching yet.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/01_beginner/03_multiple_nodes_linear/lesson.py

No new concept versus Lessons 1-2, this is deliberately "more of the
same" so that wiring several nodes together feels routine before
Lesson 4 introduces conditional edges (branching).
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


builder = StateGraph(GraphState)
builder.add_node("clean_text", clean_text)
builder.add_node("split_words", split_words)
builder.add_node("count_words", count_words)
builder.add_node("format_summary", format_summary)

# One straight path: START feeds clean_text, and each node's output
# becomes the next node's input, in exactly this order.
builder.add_edge(START, "clean_text")
builder.add_edge("clean_text", "split_words")
builder.add_edge("split_words", "count_words")
builder.add_edge("count_words", "format_summary")
builder.add_edge("format_summary", END)

app = builder.compile()


def main() -> None:
    result = app.invoke({"raw_text": "  LangGraph Makes Graphs Explicit  "})

    print("Cleaned text:", result["raw_text"])
    print("Words:", result["words"])
    print("Word count:", result["word_count"])
    print("Summary:", result["summary"])


if __name__ == "__main__":
    main()
