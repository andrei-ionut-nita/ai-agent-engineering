# Lesson 10: Structured Output

## Why "ask nicely" isn't enough

You could prompt any model with "reply in JSON with keys title, year,
and director" and most of the time, with a capable model, it would
work. "Most of the time" is the problem: a real program parsing that
reply needs it to work *every* time, and free-form prompting gives you
no actual guarantee, just a good habit the model has picked up from
training.

Ollama's `format` parameter solves this properly: instead of hoping
the model formats its answer correctly, it constrains generation
itself so the model is structurally unable to produce a token that
would break the schema. This is the same idea behind LangChain's
`with_structured_output()` and pydantic_ai's typed outputs, just
happening locally against your own model.

## The code, piece by piece

```python
class Movie(BaseModel):
    title: str
    year: int
    director: str
```

An ordinary Pydantic model, nothing Ollama-specific about it. This is
the exact same tool the pydantic_ai course builds an entire course
around, and it's already part of this project's dependencies.

```python
response = ollama.chat(
    model="llama3.2",
    messages=[...],
    format=Movie.model_json_schema(),
    options={"temperature": 0},
)
```

`Movie.model_json_schema()` turns the class definition into a JSON
Schema dict, a format both Pydantic and Ollama understand.
`temperature=0` is a sensible default here, from Lesson 6, extraction
tasks like this want a steady, most-likely answer, not creative
variation.

```python
movie = Movie.model_validate_json(response.message.content)
```

Because the schema constrained what the model could generate,
`response.message.content` is guaranteed valid JSON matching `Movie`'s
shape. Parsing it back into a real `Movie` object should never raise a
validation error the way parsing arbitrary free-form text would.

## A note on speed

Constrained decoding has real overhead: the model has to check, at
every single token, which continuations are still legal under the
schema. For small, simple schemas like this one it's barely
noticeable; very large or deeply nested schemas can measurably slow
generation down. Worth knowing before you reach for `format` on a
huge, complicated schema and wonder why it's suddenly slow.

## Running it

```bash
uv run python lessons/ollama/02_intermediate/10_structured_output/lesson.py
```

## Expected output

```
Raw JSON from the model: {"title": "Inception", "year": 2010, "director": "Christopher Nolan"}

Parsed into a real Movie object: title='Inception' year=2010 director='Christopher Nolan'
movie.year is an actual int: 2011
```

With `temperature=0`, this should be identical (or very close to it)
every time you run it, unlike most other lessons so far.

## Checkpoint

- **`format=<json schema>`**: constrains generation so the output is
  structurally guaranteed to match the schema, not just prompted to.
- **Why it's stronger than prompting**: the model can't generate a
  token that would break the schema, there's no "usually works" here.
- **`Movie.model_json_schema()`**: Pydantic already knows how to
  produce the schema Ollama needs, no extra library required.
- **Tradeoff**: constrained decoding has overhead, larger schemas can
  measurably slow generation.

If anything here still feels unclear, ask before moving to Lesson 11.
