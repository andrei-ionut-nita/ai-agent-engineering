"""
Lesson 24: structured output inside a graph node.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/03_advanced/24_structured_output_in_a_graph/lesson.py

with_structured_output is the same call the langchain course used at the
top level (langchain course, lesson 18). Here it lives inside one node
of a graph, and a downstream node reads the structured fields it wrote
into state to decide how to respond, same idea as Lesson 4's conditional
routing, just routing on fields the model itself extracted.
"""

from typing import Literal

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

load_dotenv()


class FeedbackAnalysis(BaseModel):
    """The schema we ask the model to fill in. Same idea as Lesson 24's
    (langchain course) Pydantic models, just consumed by a graph node
    instead of a top-level chain."""

    topic: str = Field(description="The single main subject of the feedback, in a few words.")
    sentiment: Literal["positive", "negative", "neutral"] = Field(
        description="The overall sentiment of the feedback."
    )


class State(TypedDict):
    # messages carries the raw conversation, same as MessagesState.
    # topic/sentiment are new fields this graph adds to hold the
    # structured extraction, plain str fields with no reducer, so each
    # node that writes them simply replaces the previous value.
    messages: list
    topic: str
    sentiment: str


model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
structured_model = model.with_structured_output(FeedbackAnalysis)


def extract(state: State) -> dict:
    # The structured model returns a FeedbackAnalysis instance directly,
    # not an AIMessage, there are no tool calls or .text to unwrap here.
    last_user_message = state["messages"][-1].content
    analysis = structured_model.invoke(last_user_message)
    return {"topic": analysis.topic, "sentiment": analysis.sentiment}


def respond(state: State) -> dict:
    # This node never re-reads the raw text, it only trusts the
    # structured fields the previous node already extracted, exactly
    # like routing on any other piece of state (Lesson 4).
    if state["sentiment"] == "negative":
        reply = (
            f"I'm sorry to hear about the trouble with {state['topic']}. "
            "I've flagged this for follow-up."
        )
    elif state["sentiment"] == "positive":
        reply = f"Glad to hear {state['topic']} is working well for you!"
    else:
        reply = f"Thanks for the note about {state['topic']}."
    return {"messages": [reply]}


builder = StateGraph(State)
builder.add_node("extract", extract)
builder.add_node("respond", respond)
builder.add_edge(START, "extract")
builder.add_edge("extract", "respond")
builder.add_edge("respond", END)
app = builder.compile()


def main() -> None:
    for feedback in [
        "The new checkout flow keeps crashing on the payment step, very frustrating.",
        "Loving the redesigned dashboard, it's so much faster now.",
    ]:
        result = app.invoke({"messages": [HumanMessage(feedback)], "topic": "", "sentiment": ""})
        print(f"Feedback: {feedback}")
        print(f"  Extracted: topic={result['topic']!r} sentiment={result['sentiment']!r}")
        print(f"  Reply: {result['messages'][-1]}\n")


if __name__ == "__main__":
    main()
