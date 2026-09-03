"""
Lesson 3: declaring one tool, letting Gemini request a call to it, and
reading the request back out of the response.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/agentic_rag/01_beginner/03_gemini_function_calling_basics/lesson.py
"""

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

CHAT_MODEL = "gemini-3.5-flash-lite"

# A FunctionDeclaration is a description of a Python function written
# in a schema Gemini can read, not the function itself. Gemini never
# runs this code, it only ever proposes calling it by name with
# specific arguments; this course's own code is what actually runs it
# (Lesson 5 does that part).
GET_TEMPERATURE_DECLARATION = types.FunctionDeclaration(
    name="get_current_temperature",
    description="Get the current outdoor temperature for a named city.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "city": types.Schema(
                type=types.Type.STRING,
                description="The city to look up, e.g. 'Lisbon'.",
            ),
        },
        required=["city"],
    ),
)

# A Tool bundles one or more FunctionDeclarations together; this course
# starts with exactly one.
WEATHER_TOOL = types.Tool(function_declarations=[GET_TEMPERATURE_DECLARATION])


def main() -> None:
    question = "What's the temperature in Lisbon right now?"

    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=question,
        config=types.GenerateContentConfig(tools=[WEATHER_TOOL]),
    )

    print(f"Q: {question}\n")

    # response.function_calls is a convenience shortcut over
    # response.candidates[0].content.parts, pulling out just the parts
    # that are function-call requests, if any exist.
    calls = response.function_calls
    if calls:
        for call in calls:
            print(f"Gemini did NOT answer directly. It requested a tool call instead:")
            print(f"  name: {call.name}")
            print(f"  args: {call.args}")
        print(
            "\nGemini has no live weather feed, and no way to actually get this\n"
            "number, so instead of guessing, it asked to call a function it was\n"
            "told exists. Nothing was executed: no HTTP request happened, no\n"
            "code ran. This response is just a structured request, name and\n"
            "arguments, waiting for something outside Gemini to fulfill it and\n"
            "hand the result back. That's Lesson 5's job."
        )
    else:
        print(f"Gemini answered directly, no tool call requested: {response.text}")


if __name__ == "__main__":
    main()
