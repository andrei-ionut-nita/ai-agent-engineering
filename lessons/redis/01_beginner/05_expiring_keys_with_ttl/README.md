# Lesson 5: `SETEX`, `EXPIRE`, caching an LLM response for a while

## Where we left off

Every key set in Lesson 4 lives forever, until something explicitly
deletes it. That's wrong for a cache: a cached answer that's never
allowed to go stale is just a bug waiting to serve outdated
information. This lesson adds a lifespan to a key.

## `SETEX`: set and expire in one call

```python
r.setex("cache:capital_of_france", 60, "Paris")
```

`SETEX key seconds value` is `SET` plus an expiry, in one atomic call:
the key is set, and Redis guarantees it disappears on its own after
`seconds` pass, no cron job or cleanup script required. This is the
shape a response cache takes throughout this course: cache the answer,
give it a TTL (time-to-live) that matches how long it's safe to reuse.

## `EXPIRE`: adding a TTL after the fact

```python
r.set("session:abc123", "active")
r.expire("session:abc123", 300)
```

`EXPIRE key seconds` attaches a TTL to a key that's already set,
useful when the value and its lifespan come from different places in
your code (Lesson 8's checkpoint sets a session hash, then separately
decides how long it should live).

## Checking and clearing a TTL

```python
r.ttl("session:abc123")   # seconds remaining, or -1 (no TTL), or -2 (gone)
r.persist("session:abc123")  # removes the TTL, key lives forever again
```

`TTL` is useful for debugging (is this key about to expire when I
didn't expect it to?) and for building on top of, Lesson 10's rate
limiter reads it directly to know how long until a counter resets.

## Why this matters for an LLM response cache

An LLM call costs money and time. If the same prompt is likely to
repeat (a common question, a repeated tool lookup), caching its answer
under a TTL means a repeat within that window is a single `GET` instead
of a full model call, while still guaranteeing the cache can't serve a
stale answer forever. Lesson 9 builds this into a real cache keyed by a
hash of the prompt; this lesson is the TTL mechanics underneath it.

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/01_beginner/05_expiring_keys_with_ttl/lesson.py
```

## Expected output

```
SETEX cache:capital_of_france 60 'Paris'
TTL right after SETEX: 60
GET before expiry: 'Paris'
TTL after EXPIRE 1: 1
GET after 1.5s sleep: None
```

## Checkpoint

- **`SETEX key seconds value`**: set and add a TTL in one atomic call,
  the shape a response cache uses.
- **`EXPIRE key seconds`**: attach a TTL to an already-set key.
- **`TTL key`**: seconds remaining, `-1` if no TTL, `-2` if the key is
  gone (expired or never existed).

If anything here still feels unclear, ask before moving to Lesson 6.
