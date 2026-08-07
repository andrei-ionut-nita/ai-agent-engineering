"""
Lesson 13: dropping Ollama into LangChain with ChatOllama.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/02_intermediate/13_swapping_into_langchain/lesson.py

This is the payoff of the langchain course's Lesson 11
(init_chat_model): swapping providers really is this small a change,
here shown against a local model instead of a second cloud provider.
"""

from langchain_core.tools import tool
from langchain_ollama import ChatOllama


# ChatOllama is a LangChain chat model class, same base class as
# ChatGoogleGenerativeAI from every other course. Same .invoke(), same
# .bind_tools(), same message objects back, just pointed at your local
# Ollama server instead of Google's API.
model = ChatOllama(model="llama3.2", temperature=0)


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    fake_weather = {"Paris": "18C, cloudy", "Tokyo": "25C, sunny"}
    return fake_weather.get(city, "unknown city")


def main() -> None:
    # .invoke() works exactly like every langchain lesson: a plain string
    # in, an AIMessage back.
    response = model.invoke("In one sentence, what is Python used for?")
    print(f"Plain call: {response.text}")
    print(f"AIMessage type: {type(response).__name__}\n")

    # bind_tools() is the exact same method used against Gemini in the
    # langchain course's tool-calling lessons. LangChain translates the
    # @tool-decorated function into whatever format ChatOllama's provider
    # (Ollama) actually expects underneath, the same abstraction that
    # makes swapping providers possible at all.
    model_with_tools = model.bind_tools([get_weather])
    tool_response = model_with_tools.invoke("What is the weather in Paris?")
    print(f"Tool call requested: {tool_response.tool_calls}")


if __name__ == "__main__":
    main()
