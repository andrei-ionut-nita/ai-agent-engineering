"""
Lesson 20: Command, updating state and routing in one step.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/02_intermediate/20_command_objects/lesson.py

Lesson 4 split "update state" and "decide where to go next" into two
separate mechanisms: a node returns a dict, then a SEPARATE
add_conditional_edges call inspects state afterward to pick the next
node. Command collapses both into one: a node can return a Command that
updates state AND names the next node, in a single return value, no
add_conditional_edges call needed for that node's routing at all.
"""

from typing import Literal

from typing_extensions import TypedDict

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


class ReviewState(TypedDict):
    review_text: str
    sentiment: str
    response: str


def classify_and_route(state: ReviewState) -> Command[Literal["handle_positive", "handle_negative"]]:
    # This node does the classifying work a Lesson 4 node would do, but
    # instead of returning a dict and leaving routing to a separate
    # add_conditional_edges call, it decides the destination itself,
    # right here, in the same place it computes the classification.
    verdict = model.invoke(
        f"Is this review positive or negative? Reply with exactly one word, "
        f"'positive' or 'negative'.\n\nReview: {state['review_text']}"
    ).text.strip().lower()

    if "positive" in verdict:
        return Command(update={"sentiment": "positive"}, goto="handle_positive")
    return Command(update={"sentiment": "negative"}, goto="handle_negative")


def handle_positive(state: ReviewState) -> dict:
    return {"response": "Thank you for the kind words! We're thrilled you enjoyed it."}


def handle_negative(state: ReviewState) -> dict:
    return {"response": "We're sorry to hear that. A team member will follow up with you."}


builder = StateGraph(ReviewState)
builder.add_node("classify_and_route", classify_and_route)
builder.add_node("handle_positive", handle_positive)
builder.add_node("handle_negative", handle_negative)

builder.add_edge(START, "classify_and_route")
# Notice: no add_conditional_edges call for classify_and_route's output.
# The Command object it returns already said where to go, that IS the
# routing, add_edge is only still needed for the two nodes that always
# lead straight to END.
builder.add_edge("handle_positive", END)
builder.add_edge("handle_negative", END)

app = builder.compile()


def main() -> None:
    reviews = [
        "This product exceeded my expectations, I use it every single day!",
        "Terrible experience, it broke after two uses and support never replied.",
    ]

    for review in reviews:
        result = app.invoke({"review_text": review, "sentiment": "", "response": ""})
        print(f"Review: {review}")
        print(f"  Sentiment (set by Command's update): {result['sentiment']}")
        print(f"  Response (from the node Command routed to): {result['response']}\n")


if __name__ == "__main__":
    main()
