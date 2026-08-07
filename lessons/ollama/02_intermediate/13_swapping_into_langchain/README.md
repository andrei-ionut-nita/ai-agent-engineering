# Lesson 13: Swapping Ollama Into LangChain

## The payoff from langchain Lesson 11

The langchain course's Lesson 11 (`init_chat_model`) made a promise:
LangChain's whole point is that swapping AI providers means changing a
line or two, not rewriting your program. This lesson cashes that
promise in for real, against a genuinely different kind of provider,
a local model instead of a second cloud one.

`ChatOllama`, from the `langchain-ollama` package, is a LangChain chat
model class, the same family as `ChatGoogleGenerativeAI` used
everywhere else in this repo. Same `.invoke()`, same `.bind_tools()`,
same `AIMessage` objects back. The only thing that changes is which
class you instantiate and what's underneath it.

## The code, piece by piece

```python
model = ChatOllama(model="llama3.2", temperature=0)
```

Compare this to `ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")`
from langchain Lesson 1: same shape, no API key needed here for the
reason covered back in Lesson 3 of this course, there's no remote
provider to authenticate against.

```python
response = model.invoke("In one sentence, what is Python used for?")
response.text
```

Identical to every other LangChain lesson in this repo. `response` is
a real `AIMessage`, `.text` pulls out the written reply, exactly the
same as calling Gemini.

```python
@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    ...

model_with_tools = model.bind_tools([get_weather])
tool_response = model_with_tools.invoke("What is the weather in Paris?")
```

This is the langchain course's `@tool` and `.bind_tools()` pattern
(Lessons 13-14 there), completely unchanged. LangChain translates the
decorated function into whatever tool-calling format Ollama actually
expects (the same shape as Lesson 11's raw `TOOLS` dict in this
course), so you never write that translation yourself.

## Why reach for this instead of the raw `ollama` package

Lessons 3-12 used the `ollama` package directly, and that's a
perfectly good choice for a program that only ever needs to talk to
Ollama. `ChatOllama` earns its place when you want the option to swap
providers later without a rewrite (development against a free local
model, production against a more capable cloud one, say), or when your
agent is already built with LangChain's abstractions (chains,
LangGraph nodes, MCP tool adapters) and Ollama needs to slot into that
same shape.

## Running it

```bash
uv run python lessons/ollama/02_intermediate/13_swapping_into_langchain/lesson.py
```

## Expected output

```
Plain call: Python is a versatile and widely-used programming language that is used for various purposes, including web development, data analysis, machine learning, automation, and more, due to its simplicity, readability, and large community of developers who contribute to its extensive libraries and frameworks.
AIMessage type: AIMessage

Tool call requested: [{'name': 'get_weather', 'args': {'city': 'Paris'}, 'id': '...', 'type': 'tool_call'}]
```

The `id` field is a random UUID LangChain generates for each tool call
and will differ every run; `name` and `args` should always read
`get_weather` and `{'city': 'Paris'}`.

## Checkpoint

- **`ChatOllama`**: a LangChain chat model class for Ollama, same base
  interface as `ChatGoogleGenerativeAI`.
- **`.invoke()` and `.bind_tools()`**: identical usage to every other
  course in this repo, LangChain hides the provider-specific details.
- **When to prefer this over the raw `ollama` package**: when you want
  provider swappability, or your agent already uses LangChain's
  abstractions elsewhere.

If anything here still feels unclear, ask before moving to Lesson 14.
