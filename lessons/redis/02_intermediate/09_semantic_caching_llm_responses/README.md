# Lesson 9: Caching by prompt hash, cutting repeat API calls and cost

## Where we left off

Lesson 5 gave a key a TTL. This lesson uses exactly that mechanic for
its real purpose in an agent system: not calling an LLM twice for the
same question.

## A note on "semantic" here

This lesson caches by an exact hash of the prompt text, not by
meaning, two prompts that ask the same thing in different words won't
share a cache entry. True embedding-similarity caching needs a vector
index to find "close enough" prompts, exactly what Lesson 17 builds.
This lesson is the simpler, still very useful, half: an identical
prompt (a repeated tool call, a user re-asking the same question, a
retry after a transient error) is common enough on its own to be worth
short-circuiting.

## No model calls in this course

Every lesson that talks about "an LLM response" or "an agent" in this
course simulates the expensive step with a deliberately slow local
function instead of a real API call, so nothing here needs a
`GOOGLE_API_KEY`. The point is Redis's own mechanics, hashing, TTLs,
pub/sub, streams, not the model behind them; wiring a real
`ChatGoogleGenerativeAI` call in is a one-line swap once the caching
logic itself is understood.

```python
def expensive_llm_call(prompt: str) -> str:
    time.sleep(1.5)  # stands in for a real network round trip
    return f"Answer to: {prompt}"
```

## Hashing the prompt into a cache key

```python
import hashlib

def cache_key(prompt: str) -> str:
    digest = hashlib.sha256(prompt.encode()).hexdigest()
    return f"cache:llm:{digest}"
```

Hashing, rather than using the raw prompt as the key, keeps keys a
fixed, short length regardless of how long the prompt is, and sidesteps
any characters in the prompt that wouldn't be safe or sensible inside a
Redis key.

## Check-then-call-then-store

```python
def cached_call(r, prompt: str, ttl_seconds: int) -> tuple[str, bool]:
    key = cache_key(prompt)
    cached = r.get(key)
    if cached is not None:
        return cached, True

    answer = expensive_llm_call(prompt)
    r.setex(key, ttl_seconds, answer)
    return answer, False
```

This is the whole pattern: look for the key first, return immediately
on a hit, only pay the expensive call on a miss, and store the result
with a TTL so a stale answer can't linger forever. The `bool` returned
alongside the answer just makes it easy to see, in this lesson's
output, which calls were served from cache.

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/02_intermediate/09_semantic_caching_llm_responses/lesson.py
```

## Expected output

```
Call 1 (What is the capital of France?): MISS, took 1.5s
Call 2 (What is the capital of France?): HIT, took 0.0s
Call 3 (What is the capital of Germany?): MISS, took 1.5s
```

## Checkpoint

- **caching by prompt hash**: an exact-match cache, `hashlib.sha256`
  turns any prompt into a fixed-length key.
- **check-then-call-then-store**: `GET` first, only call the expensive
  function on a miss, `SETEX` the result with a TTL.
- **"semantic" vs. exact-match**: this lesson matches identical
  prompts only; matching by meaning needs a vector index, built in
  Lesson 17.

If anything here still feels unclear, ask before moving to Lesson 10.
