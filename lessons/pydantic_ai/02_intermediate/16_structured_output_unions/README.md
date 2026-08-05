# Lesson 16: Structured output unions

## Letting the agent choose its own response shape

Lesson 3 gave an agent exactly one possible output shape. Real agents
often need to pick between several: "answer the question" or "ask a
clarifying question," "return search results" or "return an error
explanation." `output_type` accepts a `Union` of models for exactly
this:

```python
class WeatherAnswer(BaseModel):
    kind: str = "weather"
    forecast: str

class JokeAnswer(BaseModel):
    kind: str = "joke"
    text: str

agent = Agent(
    "google:gemini-3.5-flash-lite",
    output_type=WeatherAnswer | JokeAnswer,
)
```

Pydantic AI turns the union into two candidate schemas the model can
choose between, and `result.output` comes back as a real instance of
whichever one the model picked, not a dict you have to inspect and
branch on yourself:

```python
result = agent.run_sync("Tell me a joke.")
match result.output:
    case JokeAnswer(text=text):
        print("Joke:", text)
    case WeatherAnswer(forecast=forecast):
        print("Forecast:", forecast)
```

## Why this beats a single "kind" field on one model

You could instead define one `BaseModel` with an optional field for
every possible answer type, but then every consumer has to remember
which fields are actually populated for a given `kind`. A `Union` makes
"this is a `JokeAnswer`, so it has `.text` and nothing else" a fact
your type checker verifies, not a convention you hope holds.

## Running it

```bash
uv run python lessons/pydantic_ai/02_intermediate/16_structured_output_unions/lesson.py
```

## Checkpoint

- `output_type=ModelA | ModelB` lets the agent choose which shape to
  return, still fully validated either way.
- `result.output`'s runtime type tells you which branch the model
  took; `isinstance`/`match` on it is the idiomatic way to handle each
  case.
- This avoids one bloated model with a "kind" field and a pile of
  optional attributes.

If anything here still feels unclear, ask before moving to Lesson 17,
where control flow itself becomes an explicit graph.
