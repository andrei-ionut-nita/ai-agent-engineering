# Lesson 21: Retries and rate limits

## Where this lesson actually comes from

This isn't a hypothetical concern. While building this course, real
calls to the live Gemini API hit real `429` ("you've exceeded your
quota") and `503` ("the model is temporarily overloaded") errors,
multiple times. Those aren't bugs in any code, they're the API itself
saying "not right now." This lesson is about handling that gracefully,
instead of letting it crash your program.

## Transient failures vs. Lesson 16's failures

Lesson 16 handled a tool call that was simply *wrong* (dividing by
zero), no amount of retrying fixes that, the math is undefined no
matter how many times you ask. A `429` or `503` is different: it's
**transient**, the request itself was fine, the service just couldn't
handle it *right at that moment*. Waiting a bit and trying again often
just works.

## A manual retry loop

```python
def retry_with_backoff(func, *args, max_attempts: int = 5) -> str:
    wait_seconds = 0.5
    for attempt in range(1, max_attempts + 1):
        try:
            return func(*args)
        except Exception as error:
            if attempt == max_attempts:
                raise
            print(f"  Attempt {attempt} failed ({error}), waiting {wait_seconds}s...")
            time.sleep(wait_seconds)
            wait_seconds *= 2
```

This wraps any function call: try it, and if it raises, wait, then try
again, up to `max_attempts` times. If every attempt fails, the last
exception is finally allowed to raise for real, we don't retry forever.

Notice `wait_seconds *= 2`, the wait time **doubles** after each
failure (0.5s, then 1s, then 2s, then 4s...). This is called
**exponential backoff**, and it matters for a real reason: if a server
is overloaded and everyone's code retries instantly, over and over, that
just makes the overload worse. Waiting progressively longer gives the
server room to recover.

The lesson tests this against `flaky_operation`, a fake function that
fails twice, then succeeds on the third try, standing in for a real
transient failure without needing to actually exhaust a real API quota
just to demonstrate the concept.

## You've already seen the real thing at work

```python
model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", max_retries=3)
```

LangChain's chat models already have retry logic like this **built in**.
`max_retries` controls how many times a failed request gets automatically
retried before the error is finally raised to your code.

In fact, you've already seen this exact mechanism working, or rather,
failing loudly when it ran out of retries: every full error traceback
from a real API failure earlier in this course mentioned a library
called `tenacity`, that's what implements these automatic retries
underneath `ChatGoogleGenerativeAI`. When you saw a `429` error crash a
script earlier, what actually happened is tenacity retried a few times
automatically, first, and only raised the error to us after it ran out
of attempts.

## Running it

```bash
uv run python lessons/langchain/02_intermediate/21_retries_and_rate_limits/lesson.py
```

## Checkpoint

- **transient failure**: a request that failed for reasons unrelated to
  whether it was correct (rate limits, temporary overload), where
  retrying often succeeds.
- **exponential backoff**: waiting progressively longer between retries,
  so retrying doesn't make an overloaded server's problem worse.
- **`max_retries`**: LangChain's chat models already retry transient
  failures automatically, via the `tenacity` library, before ever
  raising an error to your code.

If anything here still feels unclear, ask before moving to Lesson 22,
the Intermediate tier's checkpoint project.
