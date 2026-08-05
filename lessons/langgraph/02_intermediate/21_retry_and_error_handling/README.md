# Lesson 21: RetryPolicy, a node that recovers from failure automatically

## Real nodes fail sometimes

Every node in this course so far has assumed the world cooperates: the
model answers, the tool returns, nothing times out. Real nodes call
things that occasionally fail for reasons that have nothing to do with
your code being wrong, an API briefly overloaded, a network blip, a
service restarting. `RetryPolicy` tells LangGraph to retry a node
automatically when that happens, instead of you writing a manual
try/except/retry loop around every flaky call.

## Attaching a retry policy to a node

```python
retry_builder.add_node(
    "unreliable_call",
    unreliable_call,
    retry_policy=RetryPolicy(max_attempts=3, initial_interval=0.1),
)
```

`retry_policy` is just another keyword argument to `add_node`, no
separate wiring step needed. `max_attempts=3` means: try once, and on
failure, retry up to two more times (three attempts total), waiting
`initial_interval` seconds before the first retry and backing off from
there (`backoff_factor`, default `2.0`, doubles the wait each time), all
before finally letting the exception propagate for real if every attempt
fails.

## Not every exception gets retried

```python
class FlakyServiceError(Exception):
    """..."""
```

This lesson deliberately does not raise a plain `ValueError`. Verified
directly against this project's installed LangGraph: its default
`retry_on` policy explicitly excludes `ValueError`, `TypeError`,
`KeyError`-style lookup errors, and several others, on the reasoning
that those usually mean your code or input is genuinely wrong, and
retrying broken logic just fails the same way three times instead of
once. Only things that look like transient infrastructure failures
(connection errors, 5xx HTTP responses, or, as here, a custom exception
type outside that exclusion list) get retried by default. You can pass
your own `retry_on=` to `RetryPolicy` (a type, a tuple of types, or a
function) if you need different rules.

## A deterministic demo, on purpose

```python
attempt_count = 0

def unreliable_call(state: dict) -> dict:
    global attempt_count
    attempt_count += 1
    if attempt_count < 3:
        raise FlakyServiceError(f"simulated failure on attempt {attempt_count}")
    return {"result": "success"}
```

A module-level counter, not `random`, decides when the call "succeeds."
This makes the lesson's output identical every time you run it: fails on
attempts 1 and 2, succeeds on attempt 3, always.

## The same failure, with no retry policy, for contrast

```python
no_retry_builder.add_node("unreliable_call", unreliable_call)  # no retry_policy=
...
try:
    app_without_retry.invoke({"result": ""})
except FlakyServiceError as exc:
    print(f"  Uncaught after the FIRST attempt: {exc!r}")
```

Without `retry_policy=`, the very first failure propagates straight out
of `.invoke()` as a real, uncaught exception, no second attempt ever
happens. This script wraps that call in a `try`/`except` only so the
demo can finish and make its point clearly, a real caller would need to
actually decide how to handle that failure, log it, alert someone, fall
back to something else.

## Running it

```bash
uv run python lessons/langgraph/02_intermediate/21_retry_and_error_handling/lesson.py
```

You'll see the retry-policy version succeed on its third attempt, then
the no-retry version fail immediately on its first, same underlying
flaky function both times.

## Checkpoint

- **`RetryPolicy(max_attempts=3, ...)`**: passed to `add_node` via
  `retry_policy=`, retries a failing node automatically, with
  configurable backoff.
- **not all exceptions are retried by default**: `ValueError`,
  `TypeError`, and similar "your logic is wrong" errors are excluded;
  transient-looking failures are retried.
- **`retry_on=`**: customize which exceptions count as retryable.
- **no retry policy means the first failure is final**: the exception
  propagates straight out of `.invoke()` immediately.

If anything here still feels unclear, ask before moving to Lesson 22,
this tier's checkpoint project, which combines a persistent checkpointer,
thread-based memory, and human approval into one workflow.
