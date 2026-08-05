# Lesson 18: Structured output, reliable data instead of parsed text

## The limitation from Lesson 7

`JsonOutputParser` (Lesson 7) works by asking the model, in plain
English, to respond only with JSON, and then parsing whatever text comes
back. That's a **request**, not a guarantee. If the model ever adds a
stray sentence before the JSON, or slightly malforms it, parsing fails.
This lesson introduces a more reliable mechanism for the same goal:
getting data back in an exact shape you specify.

## Describing the shape you want

```python
from pydantic import BaseModel, Field

class MovieReview(BaseModel):
    """Structured information extracted from a movie review."""

    title: str = Field(description="The name of the movie being reviewed")
    rating_out_of_5: int = Field(description="Star rating, from 1 to 5")
    would_recommend: bool = Field(description="Whether the reviewer recommends it")
```

`BaseModel` is the same Pydantic class LangChain uses internally to
describe tool arguments (Lesson 13's `calculator.args` was built from
something like this). Here, we're using it to describe the shape of a
*final answer*: three fields, each with a type (`str`, `int`, `bool`)
and a description telling the model what that field actually means.

## Getting the model to fill it in

```python
structured_model = model.with_structured_output(MovieReview)
result = structured_model.invoke(f"Extract structured information from this review: {review_text}")
```

`.with_structured_output(MovieReview)` returns a new model-like object.
Calling `.invoke()` on it doesn't give you back an `AIMessage`, it gives
you back an actual `MovieReview` instance, already filled in and
type-checked: `result.title` is a real string, `result.rating_out_of_5`
is a real integer, `result.would_recommend` is a real boolean, not text
that merely looks like one.

## Why this is more reliable than "please respond in JSON"

Under the hood, `with_structured_output` doesn't just add a text
instruction and hope, it uses the model provider's own structured/schema
mechanism (the same underlying feature that makes tool calling reliable
in Lessons 14-16) to constrain what the model is even capable of
producing. The model isn't being politely asked to follow a format, its
output is shaped by the schema directly. This is why it's the
recommended approach whenever your code needs to reliably consume a
model's answer, rather than just display it to a human.

## What you get for free: type checking

```python
assert isinstance(result.rating_out_of_5, int)
```

Because `result` is a real Pydantic object, your editor and any type
checker you run know its fields' types ahead of time. Typo a field name
(`result.rating` instead of `result.rating_out_of_5`) and that's an
error your tools can catch before you even run the code, unlike a typo'd
dictionary key from `JsonOutputParser`, which would only surface as a
runtime `KeyError`, if you're unlucky enough to hit that code path
during testing at all.

## Running it

```bash
uv run python lessons/langchain/02_intermediate/18_structured_output/lesson.py
```

## Checkpoint

- **Pydantic `BaseModel`**: describes an exact data shape, field names,
  types, and descriptions, reused here for a final answer instead of a
  tool's arguments.
- **`.with_structured_output(Schema)`**: returns a model-like object
  whose `.invoke()` returns a real instance of `Schema`, not an
  `AIMessage`.
- **why it's more reliable**: constrains what the model can produce,
  rather than just asking nicely and hoping the text parses.

If anything here still feels unclear, ask before moving to Lesson 19.
