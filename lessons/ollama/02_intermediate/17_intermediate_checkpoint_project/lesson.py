"""
Lesson 17 (Checkpoint): a tool-calling local agent, zero cloud calls.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/02_intermediate/17_intermediate_checkpoint_project/lesson.py

This combines everything from the intermediate tier: tool calling
(Lesson 11) inside a growing, multi-turn messages list (Lesson 12),
looped until the model stops asking for tools. No structured output,
LangChain, or pydantic_ai here on purpose, this is the raw ollama
package doing the whole job by itself.
"""

import ollama


def get_weather(city: str) -> str:
    fake_weather = {"Paris": "18C, cloudy", "Tokyo": "25C, sunny"}
    return fake_weather.get(city, "unknown city")


def calculate(expression: str) -> str:
    try:
        # A real tool would use a safe expression parser, not eval(). This
        # stays minimal on purpose since arithmetic tools aren't the point
        # of this lesson, the agent loop around them is.
        return str(eval(expression, {"__builtins__": {}}))
    except Exception as exc:
        return f"error: {exc}"


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a basic arithmetic expression",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    },
]

FUNCTIONS = {"get_weather": get_weather, "calculate": calculate}


def run_agent(messages: list[dict]) -> str:
    # Looped, not a single ask/call/respond round trip like Lesson 11: a
    # question might need zero, one, or several tool calls before the
    # model is ready to write a final answer, so this keeps calling
    # ollama.chat() until a reply comes back with no tool_calls at all.
    while True:
        response = ollama.chat(model="llama3.2", messages=messages, tools=TOOLS)
        messages.append(response.message)

        if not response.message.tool_calls:
            return response.message.content

        for call in response.message.tool_calls:
            function = FUNCTIONS[call.function.name]
            result = function(**call.function.arguments)
            messages.append({"role": "tool", "content": result, "tool_name": call.function.name})


def main() -> None:
    # One messages list for the whole conversation (Lesson 12's pattern),
    # reused across three separate questions.
    messages: list[dict] = []

    messages.append({"role": "user", "content": "What is the weather in Tokyo?"})
    print(f"Q1: What is the weather in Tokyo?\nA1: {run_agent(messages)}\n")

    messages.append({"role": "user", "content": "What is 47 * 12?"})
    print(f"Q2: What is 47 * 12?\nA2: {run_agent(messages)}\n")

    # This last question needs BOTH the tool-calling loop AND real memory
    # of the first question's answer, tying the whole tier together.
    messages.append(
        {"role": "user", "content": "Was the city I asked about earlier warmer or colder than 20 degrees?"}
    )
    print(f"Q3: Was the city I asked about earlier warmer or colder than 20 degrees?\nA3: {run_agent(messages)}")


if __name__ == "__main__":
    main()
