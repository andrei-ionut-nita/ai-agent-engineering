# Lesson 13: Structured agent state beyond flat strings, via `RedisJSON`

## Where we left off

A hash (Lesson 6) holds flat field/value pairs, no nesting: a field's
value is always a string. Agent state is often nested, a tool call's
arguments, a list of sources inside a result, a plan made of steps.
`RedisJSON` (one of the modules `redis-stack-server` bundles, confirmed
loaded back in Lesson 2) stores and queries real JSON, nesting
included.

## Setting a document

```python
r.json().set("agent:plan:abc123", "$", {
    "goal": "research the weather in three cities",
    "steps": [
        {"city": "Paris", "done": True},
        {"city": "Berlin", "done": False},
        {"city": "Madrid", "done": False},
    ],
})
```

`r.json()` returns a JSON-specific command group on the client, mirroring
`redis-py`'s pattern for `r.ft()` (Lessons 17-18). `$` is JSONPath for
"the whole document", `SET key $ value` replaces it entirely, the JSON
equivalent of Lesson 4's plain `SET`.

## Reading and writing one field, not the whole document

```python
r.json().get("agent:plan:abc123", "$.goal")
r.json().set("agent:plan:abc123", "$.steps[1].done", True)
```

This is what a hash can't do: `$.steps[1].done` reaches directly into
the second step of a nested list and flips one boolean, without
reading the whole document into Python, editing it, and writing it all
back. The path syntax is JSONPath, the same idea as a file path, just
addressing a location inside a document instead of a filesystem.

## Atomic numeric updates, inside a document

```python
r.json().numincrby("agent:plan:abc123", "$.steps[1].retries", 1)
```

`JSON.NUMINCRBY` is `HINCRBY`'s JSON-document equivalent: increment a
number at a path, atomically, without a read-modify-write round trip.

## When to reach for this instead of a hash

A hash is enough when your object's fields are flat and known ahead of
time (Lesson 6's session metadata). Reach for `RedisJSON` when the
state actually nests, a plan with steps, a tool call with structured
arguments, and you want Redis itself to understand that shape well
enough to update one piece of it directly.

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/02_intermediate/13_json_documents_with_redisjson/lesson.py
```

## Expected output

```
Full document: {'goal': 'research the weather in three cities', 'steps': [...]}
Goal only: ['research the weather in three cities']
Berlin done, before: False
Berlin done, after:  True
Berlin retries after NUMINCRBY: 1
```

## Checkpoint

- **`r.json().set(key, path, value)`**: writes JSON at a path, `$` means
  the whole document, matching `SET`'s role for plain strings.
- **path-scoped reads/writes**: `$.steps[1].done` updates one nested
  field directly, no read-modify-write of the whole document.
- **`JSON.NUMINCRBY`**: `HINCRBY`'s equivalent for a number nested
  inside a document.

If anything here still feels unclear, ask before moving to Lesson 14.
