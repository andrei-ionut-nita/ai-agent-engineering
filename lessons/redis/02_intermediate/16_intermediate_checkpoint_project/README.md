# Lesson 16: Intermediate Checkpoint - Cached, Rate-Limited, Streaming Chatbot

## What this is

No new concepts in this lesson. This is a checkpoint: a small, real
script built out of ideas from Lessons 9 through 15 (plus the session
memory from the Beginner tier), combined into one thing. If you can
read `lesson.py` and understand why every piece is there, you've
mastered the Intermediate tier. If any piece feels unfamiliar, that's
a sign to revisit the lesson it came from before continuing to
Advanced.

## What it does

Handles a small batch of incoming user messages for one session:
checks a rate limit before doing any work, publishes a progress event
as it starts handling each message, checks a prompt cache before
"calling the model", falls back to the (simulated) expensive call on a
miss, and appends the exchange to the session's bounded message
history. A separate subscriber prints each progress event as it
arrives, so you can see the pipeline's steps alongside its result.

## Where each piece came from

```python
count = r.incr(f"ratelimit:{user_id}")
if count == 1:
    r.expire(f"ratelimit:{user_id}", RATE_LIMIT_WINDOW_SECONDS)
if count > RATE_LIMIT_MAX_CALLS:
    ...
```
Lesson 10 (the fixed-window rate limiter), checked once per incoming
message, before any other work happens.

```python
r.publish("agent:progress", f"handling: {prompt}")
```
Lesson 11 (`PUBLISH`, a live progress event), fired at the start of
handling each message.

```python
key = f"cache:llm:{hashlib.sha256(prompt.encode()).hexdigest()}"
cached = r.get(key)
...
r.setex(key, CACHE_TTL_SECONDS, answer)
```
Lesson 9 (hash the prompt, check-then-call-then-store, `SETEX` with a
TTL).

```python
r.rpush(f"session:{session_id}:messages", message)
r.ltrim(f"session:{session_id}:messages", -MAX_HISTORY, -1)
```
Lesson 7/8 (bounded message history), unchanged from the Beginner
checkpoint.

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/02_intermediate/16_intermediate_checkpoint_project/lesson.py
```

You should see: progress events for the allowed messages printed by
the subscriber, the second occurrence of a repeated prompt served as a
cache `HIT`, and the last two messages rejected with a rate-limit
message once the batch exceeds `RATE_LIMIT_MAX_CALLS`.

## Try this yourself

Without looking anything up:

- Lower `RATE_LIMIT_MAX_CALLS` to `2` and rerun, confirm more messages
  get rejected, and that the rejected ones still don't hit the cache
  or the expensive call.
- Add a message identical to an earlier one but with different casing
  (`"What's the weather?"` vs `"what's the weather?"`), confirm it's a
  cache `MISS`, exact-hash caching is case-sensitive, exactly Lesson
  9's honest limitation.
- Subscribe to `agent:progress` from a second terminal (`redis-cli`'s
  own `SUBSCRIBE agent:progress`, no Python needed) while this script
  runs, and confirm you see the same events live.

If you can make these changes confidently, you're ready for the
Advanced tier, starting at Lesson 17.
