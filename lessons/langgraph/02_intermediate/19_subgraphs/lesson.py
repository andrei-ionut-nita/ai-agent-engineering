"""
Lesson 19: subgraphs, a whole graph used as a single node.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/02_intermediate/19_subgraphs/lesson.py

Every graph so far has been one flat set of nodes. This lesson builds a
small, self-contained "summarize" graph, compiles it, and then plugs
that compiled graph directly into a bigger parent graph as if it were an
ordinary node. From the parent's point of view, the subgraph IS a node,
same idea as agent-as-tool from the langchain course's Lesson 31, but at
the graph level instead of the agent level.
"""

from typing_extensions import TypedDict

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


# --- The subgraph: a small, self-contained 2-node summarize pipeline ---
class SummarizeState(TypedDict):
    text: str
    summary: str
    word_count: int


def summarize_node(state: SummarizeState) -> dict:
    response = model.invoke(f"Summarize this in one sentence: {state['text']}")
    return {"summary": response.text.strip()}


def count_words_node(state: SummarizeState) -> dict:
    return {"word_count": len(state["summary"].split())}


summarize_builder = StateGraph(SummarizeState)
summarize_builder.add_node("summarize_node", summarize_node)
summarize_builder.add_node("count_words_node", count_words_node)
summarize_builder.add_edge(START, "summarize_node")
summarize_builder.add_edge("summarize_node", "count_words_node")
summarize_builder.add_edge("count_words_node", END)

# Compiling it produces a runnable graph on its own, exactly like every
# other `app` in this course. It could be run standalone with .invoke().
summarize_subgraph = summarize_builder.compile()


# --- The parent graph: uses the compiled subgraph as one of its nodes ---
class ArticleState(TypedDict):
    text: str
    summary: str
    word_count: int
    title: str


def make_title(state: ArticleState) -> dict:
    response = model.invoke(f"Write a short title (5 words max) for: {state['summary']}")
    return {"title": response.text.strip()}


article_builder = StateGraph(ArticleState)

# Passing a COMPILED graph straight to add_node, instead of a plain
# function. This only works cleanly because SummarizeState's field names
# (text, summary, word_count) are a subset of ArticleState's, so the
# parent's state can flow into the subgraph and the subgraph's output can
# flow back out, with no translation function needed in between.
article_builder.add_node("summarize", summarize_subgraph)
article_builder.add_node("make_title", make_title)
article_builder.add_edge(START, "summarize")
article_builder.add_edge("summarize", "make_title")
article_builder.add_edge("make_title", END)

app = article_builder.compile()


def main() -> None:
    text = (
        "Octopuses have three hearts, blue blood, and can change both the "
        "color and texture of their skin in a fraction of a second to blend "
        "into their surroundings or communicate with other octopuses."
    )

    # From here, this call looks identical to invoking any other graph in
    # this course. Nothing about calling app.invoke() reveals that one of
    # its nodes is secretly an entire other compiled graph running inside it.
    result = app.invoke({"text": text, "summary": "", "word_count": 0, "title": ""})

    print("Summary:", result["summary"])
    print("Word count:", result["word_count"])
    print("Title:", result["title"])


if __name__ == "__main__":
    main()
