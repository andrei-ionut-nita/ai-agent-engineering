"""
Lesson 14: pointing a pydantic_ai agent at a local model.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/02_intermediate/14_swapping_into_pydantic_ai/lesson.py

Ollama has no dedicated pydantic_ai provider class. Instead, Ollama
exposes an OpenAI-compatible endpoint (http://localhost:11434/v1), so
pydantic_ai's OpenAIChatModel talks to it directly, pointed at your
local server instead of OpenAI's.
"""

from pydantic import BaseModel
from pydantic_ai import Agent, NativeOutput
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider

# OllamaProvider just fills in the base_url and a placeholder API key
# (Ollama doesn't check one, but the OpenAI-compatible client still wants
# something in that field). Everything else about OpenAIChatModel is
# unchanged from how the pydantic_ai course uses it against a real
# OpenAI-shaped provider.
model = OpenAIChatModel(
    model_name="llama3.2",
    provider=OllamaProvider(base_url="http://localhost:11434/v1"),
)


class Movie(BaseModel):
    title: str
    year: int


def main() -> None:
    # A plain, unstructured agent, same Agent class as the pydantic_ai
    # course, just backed by this local model instead of Gemini.
    plain_agent = Agent(model, system_prompt="You are a concise assistant.")
    plain_result = plain_agent.run_sync("In one sentence, what is Python used for?")
    print(f"Plain agent: {plain_result.output}\n")

    # NativeOutput asks the underlying provider's JSON-schema mode (the
    # same "format" mechanism from Lesson 10) for the structured reply,
    # instead of pydantic_ai's default of asking the model to call a
    # "return this result" tool. Smaller local models are often less
    # reliable at that default tool-based path than a real OpenAI model
    # would be, NativeOutput routes around that entirely.
    structured_agent = Agent(model, output_type=NativeOutput(Movie))
    structured_result = structured_agent.run_sync(
        "Tell me the title and release year of the movie Inception."
    )
    print(f"Structured agent: {structured_result.output!r} ({type(structured_result.output).__name__})\n")

    # A tool-using agent, same @agent.tool_plain decorator as the
    # pydantic_ai course's tool lessons.
    tool_agent = Agent(model, system_prompt="You are a weather assistant.")

    @tool_agent.tool_plain
    def get_weather(city: str) -> str:
        """Get the current weather for a city."""
        fake_weather = {"Paris": "18C, cloudy", "Tokyo": "25C, sunny"}
        return fake_weather.get(city, "unknown city")

    tool_result = tool_agent.run_sync("What is the weather in Paris?")
    print(f"Tool agent: {tool_result.output}")


if __name__ == "__main__":
    main()
