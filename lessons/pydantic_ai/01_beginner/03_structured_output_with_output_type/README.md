# Lesson 3: Structured output with `output_type`

## The problem with hoping for JSON

In `langchain`, getting structured data out of a model usually meant
either careful prompt engineering ("respond only with JSON matching
this schema...") or `with_structured_output(SomeModel)`, which works,
but is bolted onto a framework that otherwise treats output as text.

Pydantic AI makes this the default way of thinking about an agent: you
pass a Pydantic `BaseModel` as `output_type`, and `run_sync` either
returns a validated instance of it or raises. There's no separate
"structured mode", it's the same `Agent` and the same `run_sync`.

## Declaring an output type

```python
from pydantic import BaseModel
from pydantic_ai import Agent

class CityFact(BaseModel):
    city: str
    country: str
    population_millions: float

agent = Agent("google:gemini-3.5-flash-lite", output_type=CityFact)

result = agent.run_sync("Tell me about Paris.")
result.output.city              # "Paris", guaranteed to be a str
result.output.population_millions  # a float, guaranteed to parse
```

Under the hood, Pydantic AI turns `CityFact` into a JSON Schema, gives
it to the model as the required output shape, and validates whatever
comes back against the `BaseModel` before handing it to you. If the
model returns something that doesn't validate, Pydantic AI feeds the
validation error back to the model and asks it to try again (up to
`retries`, default 1), you don't have to write that retry loop
yourself.

## Why this matters more than it looks

Every field on `result.output` is a real, typed Python attribute. Your
editor autocompletes it, your type checker catches typos in it, and
downstream code (saving to a database, rendering a UI) never has to
defensively check `if "population" in parsed_json`. This is the
single biggest practical difference from `langchain`'s default string
output.

## Running it

```bash
uv run python lessons/pydantic_ai/01_beginner/03_structured_output_with_output_type/lesson.py
```

## Checkpoint

- `output_type=SomeBaseModel` makes `result.output` a validated
  instance of that model, not a string you parse yourself.
- Validation failures trigger an automatic retry with the error fed
  back to the model, up to a retry limit.
- This replaces `with_structured_output` from the langchain course, but
  as the default way agents work, not a special mode.

If anything here still feels unclear, ask before moving to Lesson 4.
