"""
Lesson 10: forcing a model's reply into a schema you can trust.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/02_intermediate/10_structured_output/lesson.py
"""

import ollama
from pydantic import BaseModel


# A plain Pydantic model, the same tool this repo's other courses use to
# describe shapes of data. Ollama doesn't need anything Ollama-specific
# here, just a JSON Schema, and Pydantic already knows how to produce one.
class Movie(BaseModel):
    title: str
    year: int
    director: str


def main() -> None:
    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": "Give me the title, release year, and director of the movie Inception.",
            }
        ],
        # format takes a JSON Schema dict. Ollama constrains generation so
        # every token it produces keeps the output valid against this
        # schema, this is much stronger than asking nicely in the prompt:
        # the model is structurally unable to return something that
        # doesn't match the shape.
        format=Movie.model_json_schema(),
        options={"temperature": 0},
    )

    raw_json = response.message.content
    print(f"Raw JSON from the model: {raw_json}")

    # Because the output is guaranteed valid against the schema, parsing
    # it back into the same Pydantic model should never raise a
    # validation error, unlike parsing free-form text and hoping.
    movie = Movie.model_validate_json(raw_json)
    print(f"\nParsed into a real Movie object: {movie}")
    print(f"movie.year is an actual int: {movie.year + 1}")


if __name__ == "__main__":
    main()
