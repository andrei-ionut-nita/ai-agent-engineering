"""
Lesson 11: tool calling with a local model, the manual ask/call/respond loop.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/02_intermediate/11_tool_calling_with_ollama/lesson.py

This is the same loop as the langchain course's manual tool-calling
lessons (13-16), and the same loop MCP wraps in a protocol (Lessons
15-16 there), just running against a local model here instead of
Gemini.
"""

import ollama

# An ordinary Python function. Nothing about it knows it's going to be
# offered to an AI, that happens entirely through the "tools" description
# below, the function itself stays plain.
def get_weather(city: str) -> str:
    fake_weather = {"Paris": "18C, cloudy", "Tokyo": "25C, sunny"}
    return fake_weather.get(city, "unknown city")


# Ollama's tool-calling format is OpenAI-compatible: a list of dicts, each
# describing one function's name, purpose, and parameter schema, exactly
# like the JSON Schema from Lesson 10, just nested under "parameters".
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "City name"}},
                "required": ["city"],
            },
        },
    }
]


def main() -> None:
    messages = [{"role": "user", "content": "What is the weather in Paris?"}]

    # First call: the model decides whether it needs a tool at all. It
    # doesn't run anything itself, it just asks for a specific call.
    response = ollama.chat(model="llama3.2", messages=messages, tools=TOOLS)
    messages.append(response.message)

    if not response.message.tool_calls:
        print(response.message.content)
        return

    # Your code, not the model, actually runs the function. The model
    # never executes anything, it only ever describes what it wants
    # called and with what arguments.
    call = response.message.tool_calls[0]
    print(f"Model wants to call: {call.function.name}({call.function.arguments})")
    result = get_weather(**call.function.arguments)
    print(f"Function returned: {result!r}")

    # The result goes back in as a "tool" role message, so the model can
    # read it and write a final, natural-language answer.
    messages.append({"role": "tool", "content": result, "tool_name": call.function.name})

    final_response = ollama.chat(model="llama3.2", messages=messages, tools=TOOLS)
    print(f"\nFinal answer: {final_response.message.content}")


if __name__ == "__main__":
    main()
