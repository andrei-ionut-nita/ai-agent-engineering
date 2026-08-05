"""
Lesson 18: structured output, reliable data instead of parsed text.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/02_intermediate/18_structured_output/lesson.py

Lesson 7's JsonOutputParser depended on the model correctly following a
text instruction ("respond only with JSON"). This lesson uses a
different mechanism that doesn't rely on the model behaving, it
constrains what the model is even allowed to produce.
"""

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


# A Pydantic model describes the exact shape of data we want back: field
# names, their types, and a description of each one. This is the same
# BaseModel class used to define tool argument schemas back in Lesson
# 13, just describing a final answer's shape instead of a tool's input.
class MovieReview(BaseModel):
    """Structured information extracted from a movie review."""

    title: str = Field(description="The name of the movie being reviewed")
    rating_out_of_5: int = Field(description="Star rating, from 1 to 5")
    would_recommend: bool = Field(description="Whether the reviewer recommends it")


# .with_structured_output() returns a NEW model-like object. Instead of
# replying with an AIMessage, calling .invoke() on it replies with an
# actual instance of MovieReview, already validated to match that shape.
structured_model = model.with_structured_output(MovieReview)


def main() -> None:
    review_text = (
        "I watched 'The Last Voyage' last night. Gorgeous visuals, but the "
        "plot dragged in the middle. Still, I'd give it 4 out of 5 stars "
        "and tell my friends to see it."
    )

    result = structured_model.invoke(
        f"Extract structured information from this review: {review_text}"
    )

    print("Result type:", type(result).__name__)
    print("Title:", result.title)
    print("Rating:", result.rating_out_of_5)
    print("Would recommend:", result.would_recommend)

    # Because this is a real Pydantic object, not a plain dict pulled out
    # of parsed text, it comes with type checking built in. This would
    # be caught immediately by your editor/type checker, not just at
    # runtime like a typo'd dictionary key would be with JsonOutputParser.
    assert isinstance(result.rating_out_of_5, int)
    assert isinstance(result.would_recommend, bool)


if __name__ == "__main__":
    main()
