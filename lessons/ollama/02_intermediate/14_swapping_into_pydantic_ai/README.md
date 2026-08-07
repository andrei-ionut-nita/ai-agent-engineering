# Lesson 14: Swapping Ollama Into pydantic_ai

## No dedicated Ollama model class, and that's fine

Unlike `ChatOllama` in Lesson 13, pydantic_ai has no
`OllamaModel` class of its own. Instead, Ollama exposes an
OpenAI-compatible endpoint at `http://localhost:11434/v1`, meaning any
client built for OpenAI's API shape can talk to it directly. pydantic_ai
already ships an `OpenAIChatModel`; `OllamaProvider` just points that
same class at your local server instead of `api.openai.com`.

```python
model = OpenAIChatModel(
    model_name="llama3.2",
    provider=OllamaProvider(base_url="http://localhost:11434/v1"),
)
```

This is a genuinely useful pattern to recognize beyond Ollama:
whenever a model provider doesn't have first-class support in a
framework you're using, check whether it exposes an OpenAI-compatible
endpoint. Many do (this is exactly the interoperability pattern that
makes cheap swapping between providers possible in the first place).

## Three agents, three pydantic_ai patterns, one local model

```python
plain_agent = Agent(model, system_prompt="You are a concise assistant.")
plain_result = plain_agent.run_sync(...)
```

An ordinary `Agent`, unstructured text output, identical usage to the
pydantic_ai course's earliest lessons.

```python
structured_agent = Agent(model, output_type=NativeOutput(Movie))
```

`output_type=Movie` alone (pydantic_ai's usual default) asks the model
to call a hidden "return this result" tool, which works well against
strong cloud models but can be less reliable on smaller local ones.
`NativeOutput(Movie)` routes around that: it uses the provider's own
JSON-schema-constrained generation instead, the exact `format`
mechanism from Lesson 10, just reached through pydantic_ai's API
instead of the raw `ollama` package. Worth knowing this option exists
specifically because local models sometimes need it.

```python
tool_agent = Agent(model, system_prompt="You are a weather assistant.")

@tool_agent.tool_plain
def get_weather(city: str) -> str:
    ...
```

`@agent.tool_plain`, unchanged from the pydantic_ai course. The same
manual ask/call/respond loop from Lesson 11 of this course, just
hidden behind pydantic_ai's decorator instead of written out by hand.

## Running it

```bash
uv run python lessons/ollama/02_intermediate/14_swapping_into_pydantic_ai/lesson.py
```

## Expected output

```
Plain agent: Python is a versatile, high-level programming language used for a wide range of applications, including web development, data analysis, machine learning, automation, and more.

Structured agent: Movie(title='Inception', year=2010) (Movie)

Tool agent: The current weather in Paris is 18 degrees Celsius with cloudy conditions. It's a pleasant day in the City of Light!
```

Wording will vary between runs. The structured agent's `year` should
usually be `2010`, small local models occasionally get real-world
facts wrong even when the *shape* of the output is guaranteed correct,
worth remembering: structured output guarantees the format, never the
accuracy.

## Checkpoint

- **No dedicated Ollama class in pydantic_ai**: use `OpenAIChatModel` +
  `OllamaProvider`, since Ollama exposes an OpenAI-compatible endpoint.
- **The OpenAI-compatible-endpoint pattern**: useful well beyond
  Ollama, for any provider without first-class framework support.
- **`NativeOutput`**: uses schema-constrained generation instead of
  pydantic_ai's default tool-based output, often more reliable on
  smaller local models.
- **Structured output guarantees shape, not truth**: valid JSON
  matching your schema can still contain a factually wrong answer.

If anything here still feels unclear, ask before moving to Lesson 15.
