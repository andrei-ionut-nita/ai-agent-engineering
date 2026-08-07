# Lesson 4: The basic key/value type, `SET` and `GET`

## Where we left off

Lesson 3 stored one string (`"greeting"`) without pausing on it. This
lesson is that pause: the string is Redis's simplest and most-used
value type, and `SET`/`GET` are the two commands most others in this
course build on top of.

## `SET` and `GET`

```python
r.set("agent:last_response", "The weather in Paris is 18C.")
value = r.get("agent:last_response")
```

`SET key value` stores `value` under `key`, overwriting whatever was
there before. `GET key` returns it, or `None` if the key doesn't exist,
there's no exception to catch, a missing key is just `None`, check for
it the same way you'd check any other Python value.

## Keys are just strings, but a naming convention pays off

Redis has no tables or schemas, every key lives in one flat namespace
per database. The `agent:last_response` style, colon-separated
segments acting like a namespace, is a convention, not a Redis feature,
but it's the one used throughout this course (and most real Redis
codebases): `agent:last_response`, `session:abc123:messages`,
`ratelimit:user42`. It makes keys readable and lets later lessons use
patterns like `session:*` to find related keys.

## A string can hold more than text

```python
r.set("agent:call_count", 0)
r.incr("agent:call_count")
```

`INCR` treats the string as an integer, increments it, and returns the
new value, atomically: two callers incrementing the same key at the
same time can't lose an update to each other, the way a Python `count
+= 1` on a shared variable could. Lesson 10's rate limiter is built
entirely on this one guarantee.

## `SET` isn't only "create"

```python
r.set("agent:last_response", "Updated answer.")
```

Calling `SET` on a key that already exists just overwrites it, there's
no separate "update" command, the same way Python's `dict[key] = value`
works whether or not `key` was already there.

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/01_beginner/04_strings_get_and_set/lesson.py
```

## Checkpoint

- **`SET`/`GET`**: store and retrieve a string by key, `GET` on a
  missing key returns `None`, no exception.
- **key naming**: `colon:separated:segments` is a convention, not a
  Redis feature, used throughout this course.
- **`INCR`**: atomically increments an integer-valued string, the
  building block for Lesson 10's rate limiter.

If anything here still feels unclear, ask before moving to Lesson 5.
