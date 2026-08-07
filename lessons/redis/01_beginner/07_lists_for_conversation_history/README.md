# Lesson 7: `RPUSH`/`LRANGE`, a chat message log

## Where we left off

A hash (Lesson 6) is great for a session's metadata, a few named
fields. A conversation isn't that shape, it's an ordered sequence of
messages that grows one at a time. Redis has a value type for that
too.

## Lists: an ordered, growable sequence

```python
r.rpush("session:abc123:messages", "user: what's the weather in Paris?")
r.rpush("session:abc123:messages", "assistant: 18C and partly cloudy.")
```

A **list** is an ordered sequence of strings under one key. `RPUSH key
value` appends to the right (tail) end, the natural direction for a
message log, each new message is pushed after the ones before it.
(`LPUSH` pushes to the left/head instead, useful when a list is being
used as a queue read from the other end, see Lesson 15.)

## Reading a range

```python
history = r.lrange("session:abc123:messages", 0, -1)
last_two = r.lrange("session:abc123:messages", -2, -1)
```

`LRANGE key start stop` returns a slice, using the same negative-index
convention as Python: `0` is the first element, `-1` is the last. `0,
-1` reads the whole list; `-2, -1` reads just the last two, the kind of
call an agent makes to pull only recent context instead of the entire
history.

## Keeping a history bounded

```python
r.ltrim("session:abc123:messages", -50, -1)
```

An unbounded chat log grows forever, and most of it stops being useful
context after a while. `LTRIM key start stop` keeps only the range
given and discards the rest, in place. Calling `LTRIM key -50 -1`
after every push keeps a list capped at its most recent 50 entries,
without a separate cleanup step.

## Length, without reading the whole list

```python
r.llen("session:abc123:messages")
```

`LLEN` returns a count in constant time, no need to `LRANGE` the whole
list just to check how many messages exist.

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/01_beginner/07_lists_for_conversation_history/lesson.py
```

## Checkpoint

- **lists**: an ordered sequence of strings, `RPUSH` appends to the
  tail, `LRANGE` reads a slice using Python-style negative indices.
- **`LTRIM`**: keeps a list capped at a bounded size, in place, no
  separate cleanup pass needed.
- **`LLEN`**: the list's length, in constant time.

If anything here still feels unclear, ask before moving to Lesson 8.
