# Lesson 11: Tool Calling With Ollama

## The same loop, running locally

The langchain course's tool-calling lessons (13-16) teach a loop: the
model reads a question, decides it needs a tool, describes which one
and with what arguments, your code actually runs it, and the result
goes back so the model can write a final answer. Some models on Ollama
support the exact same loop, over the exact same OpenAI-compatible
`tools` format, which means code you write against a local model here
transfers almost directly to any cloud provider using that convention.

Not every model on Ollama supports tool calling, it depends on how the
model was fine-tuned. `llama3.2` does; check a model's `Capabilities`
section in `ollama show <model>` (Lesson 2) if you're unsure about
another one.

## The code, piece by piece

```python
def get_weather(city: str) -> str:
    fake_weather = {"Paris": "18C, cloudy", "Tokyo": "25C, sunny"}
    return fake_weather.get(city, "unknown city")
```

A plain Python function. It has no idea it's being offered to an AI,
that connection is made entirely by the `TOOLS` description below.

```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city",
            "parameters": {"type": "object", "properties": {...}, "required": [...]},
        },
    }
]
```

A JSON Schema again, same shape as `format` in Lesson 10, just
describing a function's arguments instead of an entire reply.

```python
response = ollama.chat(model="llama3.2", messages=messages, tools=TOOLS)
```

Passing `tools=TOOLS` tells the model what's available. The model
itself never runs anything, it decides whether a tool is needed and,
if so, returns a `tool_calls` list on `response.message` describing
which function and which arguments, instead of writing a normal reply.

```python
call = response.message.tool_calls[0]
result = get_weather(**call.function.arguments)
```

Your code is the one that actually calls `get_weather`, using the
arguments the model chose. `call.function.arguments` is already a
plain dict, so `**call.function.arguments` unpacks it directly into
keyword arguments.

```python
messages.append({"role": "tool", "content": result, "tool_name": call.function.name})
final_response = ollama.chat(model="llama3.2", messages=messages, tools=TOOLS)
```

The function's return value goes back into the conversation as a
`"tool"` role message. A second call to `ollama.chat()` lets the model
read that result and write a normal, natural-language final answer.

## Running it

```bash
uv run python lessons/ollama/02_intermediate/11_tool_calling_with_ollama/lesson.py
```

## Expected output

```
Model wants to call: get_weather({'city': 'Paris'})
Function returned: '18C, cloudy'

Final answer: The current weather in Paris is 18 degrees Celsius, with cloudy skies.
```

The final sentence's exact wording will vary between runs, but it
should always mention 18 degrees and cloudy conditions, since that's
the real data the tool returned, not something the model is free to
invent.

## Checkpoint

- **`tools=TOOLS`**: describes available functions to the model using
  the same JSON Schema shape as structured output.
- **The model never runs code**: it only ever describes what it wants
  called, your program executes the actual function.
- **`response.message.tool_calls`**: how you detect the model wants a
  tool instead of writing a normal reply.
- **The `"tool"` role message**: how a function's result gets back into
  the conversation so the model can use it in a final answer.

If anything here still feels unclear, ask before moving to Lesson 12.
