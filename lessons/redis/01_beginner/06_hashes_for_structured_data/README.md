# Lesson 6: `HSET`/`HGETALL`, storing a session as a small object

## Where we left off

A plain string holds one value. A session isn't one value, it's a
small object: a user ID, when it started, how many turns it's had. You
could serialize that into JSON and store it as one string, but Redis
has a value type built for exactly this shape.

## Hashes: a key holding a small field/value map

```python
r.hset("session:abc123", mapping={
    "user_id": "u42",
    "started_at": "2026-08-07T10:00:00Z",
    "turn_count": 0,
})
```

A **hash** is one Redis key that maps to multiple field/value pairs,
like a small dict living under a single key. `HSET key mapping={...}`
sets several fields at once; a single field can also be set with `HSET
key field value`.

## Reading it back

```python
session = r.hgetall("session:abc123")
turn_count = r.hget("session:abc123", "turn_count")
```

`HGETALL key` returns the whole hash as a Python dict. `HGET key field`
reads just one field, cheaper than pulling the whole hash back when
only one piece is needed.

## Updating one field without touching the rest

```python
r.hincrby("session:abc123", "turn_count", 1)
```

`HINCRBY` is `INCR` scoped to one field of a hash, atomic the same way:
incrementing `turn_count` doesn't require reading the hash, changing it
in Python, and writing the whole thing back, which would risk two
concurrent turns clobbering each other's count.

## Why a hash, and not a JSON string

`SET key '{"user_id": "u42", "turn_count": 0}'` would work, but every
change would mean deserializing the whole string, editing one field in
Python, and re-serializing all of it, and Redis itself couldn't
increment `turn_count` atomically, it's just a string to Redis at that
point. A hash lets Redis understand the structure, so `HINCRBY` and
`HGET` operate on one field directly. (Lesson 13's `RedisJSON` module
adds a third option: real nested JSON Redis understands the *shape* of,
past a flat field/value map.)

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/01_beginner/06_hashes_for_structured_data/lesson.py
```

## Checkpoint

- **hashes**: one key mapping to multiple field/value pairs, `HSET`
  (write), `HGETALL` (read all), `HGET` (read one field).
- **`HINCRBY`**: atomically increments one field, without reading and
  rewriting the whole hash.
- A hash beats a JSON string when you need to read or update *part* of
  the structure without touching the rest.

If anything here still feels unclear, ask before moving to Lesson 7.
