# Lesson 8: Output validators and `ModelRetry`

## Beyond type validation: business-rule validation

Lesson 3's `output_type` catches shape problems, a missing field, a
string where a float was expected, automatically. But some rules
aren't about shape, they're about meaning: "the number must be
positive," "the date must be in the future," "the email domain must be
one we allow." `@agent.output_validator` is where those rules go.

```python
from pydantic_ai import RunContext, ModelRetry

@agent.output_validator
def must_be_positive(ctx: RunContext[None], output: int) -> int:
    if output <= 0:
        raise ModelRetry("The number must be positive. Try again.")
    return output
```

An output validator receives the already-type-validated output and
either returns it (possibly transformed, e.g. normalizing whitespace)
or raises `ModelRetry` with a message. That message goes straight back
to the model as feedback, and Pydantic AI asks it to produce another
answer, same as an automatic retry from a type-validation failure in
Lesson 3, just triggered by your own logic instead of Pydantic's.

## Why raise instead of returning an error value

Raising `ModelRetry` keeps the "give the model another chance" flow
uniform: type failures and business-rule failures both retry the same
way, up to the agent's `retries` limit, and both ultimately either
succeed or raise a real exception you have to handle. There's no
silent "returned `None` on failure" path to forget to check.

## Running it

```bash
uv run python lessons/pydantic_ai/01_beginner/08_output_validators_and_retries/lesson.py
```

## Checkpoint

- `@agent.output_validator` runs after type validation, for rules
  about meaning, not shape.
- Raise `ModelRetry("...")` to send feedback back to the model and get
  another attempt.
- Type-validation retries (Lesson 3) and output-validator retries
  share the same retry budget and the same underlying mechanism.

If anything here still feels unclear, ask before moving to Lesson 9,
where output starts streaming instead of arriving all at once.
