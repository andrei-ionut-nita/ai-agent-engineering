# Lesson 10: A rate limiter with `INCR` and a TTL

## Where we left off

Lesson 4's `INCR` was atomic; Lesson 5's `EXPIRE` gave a key a
lifespan. Put together, they're the entire mechanism behind rate
limiting an agent's calls, no separate library needed.

## The fixed-window counter

```python
def is_allowed(r, user_id: str, limit: int, window_seconds: int) -> bool:
    key = f"ratelimit:{user_id}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, window_seconds)
    return count <= limit
```

This is a **fixed-window** limiter, the simplest realistic version of
the idea: `INCR` a per-user counter on every call; the first call in a
fresh window also sets a TTL equal to the window's length, so the
counter resets itself once the window passes, no cleanup job needed.
If the counter is over `limit`, reject the call.

## Why the `count == 1` check matters

Only the call that creates the key should set its expiry, a call that
finds the key already there is inside an existing window and shouldn't
reset its clock. Without this check, a burst of calls late in a window
would each push the expiry further out, and the window would never
actually close, "one over `limit`" would let the count climb forever.

## What "fixed-window" trades away

A true token bucket lets a limit refill smoothly and allows a small
burst at a window boundary to even out; a fixed window can allow up to
`2 x limit` calls across two adjacent windows if they cluster right at
the boundary (a burst just before the window resets, another just
after). For per-user, per-minute limits on agent calls, that's usually
an acceptable simplification. This is the tradeoff, spelled out
honestly, not hidden behind a library name.

## Checking without incrementing

```python
r.ttl(f"ratelimit:{user_id}")
```

Useful for telling a caller how long until they can try again, without
counting the check itself as a call.

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/02_intermediate/10_rate_limiting_agent_calls/lesson.py
```

## Expected output

```
Call 1: allowed (count=1/3)
Call 2: allowed (count=2/3)
Call 3: allowed (count=3/3)
Call 4: REJECTED (count=4/3)
Seconds until reset: 5
```

## Checkpoint

- **fixed-window limiter**: `INCR` a per-user key, `EXPIRE` it only on
  the call that creates it, reject once the count exceeds `limit`.
- **the `count == 1` guard**: without it, a burst near a window
  boundary would keep pushing the window's reset out.
- **the tradeoff**: simpler than a true token bucket, at the cost of
  allowing brief bursts across a window boundary, an acceptable
  simplification for per-user agent-call limits.

If anything here still feels unclear, ask before moving to Lesson 11.
