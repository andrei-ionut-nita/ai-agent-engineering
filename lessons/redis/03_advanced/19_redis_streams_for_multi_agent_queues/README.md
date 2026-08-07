# Lesson 19: Consumer groups, durable multi-agent task handoff

## Where we left off

Lesson 15's honest limitation: a task popped with `BRPOP` and never
completed is simply gone, nothing remembers it existed. A **stream**,
Redis's log-like value type, plus a **consumer group**, fixes exactly
that: every task is tracked from delivery through acknowledgment, and
an unacknowledged one can be claimed by another worker.

## Streams: an append-only log, not a list

```python
r.xadd("stream:tasks", {"task": "summarize document 42", "priority": "high"})
```

`XADD key fields` appends an entry, Redis assigns it an ID
automatically (a timestamp plus a sequence number, unique and
increasing). Unlike a list, entries in a stream aren't removed when
read, a stream is a durable log multiple independent readers can each
work through at their own pace, closer to a message-queue topic than a
Python list.

## Consumer groups: tracking who has what

```python
r.xgroup_create("stream:tasks", "workers", id="0")
```

A **consumer group** is a named cursor over a stream, shared by
multiple consumers (workers). `id="0"` means "start this group from
the very beginning of the stream"; a group created with `id="$"`
instead would only see entries added after it was created. Every
worker in this course's examples joins the same group, `"workers"`.

## Reading as part of a group

```python
entries = r.xreadgroup("workers", "worker-1", {"stream:tasks": ">"}, count=1)
```

`XREADGROUP` reads on behalf of one named consumer (`"worker-1"`)
inside a group. `">"` means "entries never delivered to this group
before", the group remembers what it's already handed out, so two
different consumer names calling this won't receive the same entry.
Each entry read this way is marked **pending** for that consumer until
acknowledged.

## Acknowledging, and what happens if you don't

```python
r.xack("stream:tasks", "workers", entry_id)
```

`XACK` marks an entry done, removing it from the group's pending list.
An entry that's been delivered but never acknowledged, because its
worker crashed mid-task, stays visible in `XPENDING`:

```python
r.xpending("stream:tasks", "workers")
```

A real system periodically checks `XPENDING`, and reclaims entries
stuck pending too long with `XCLAIM`, handing them to a different,
still-alive worker, this lesson demonstrates the pending state,
reclaiming a stuck entry is a natural next step once this is
comfortable.

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/03_advanced/19_redis_streams_for_multi_agent_queues/lesson.py
```

## Expected output

```
Added 2 tasks to stream:tasks
worker-1 read: summarize document 42
Pending before ack: {'pending': 1, ...}
worker-1 acked summarize document 42
Pending after ack: {'pending': 0, ...}
worker-2 read: translate document 43
```

## Checkpoint

- **streams**: an append-only log, entries aren't removed on read,
  multiple consumers can each work through it independently.
- **consumer groups**: a shared, named cursor; `XREADGROUP` with `>`
  never redelivers the same entry to two different consumer names.
- **`XACK`/`XPENDING`**: acknowledgment tracking is the piece a plain
  list queue (Lesson 15) doesn't have, an unacknowledged entry stays
  visible and can be reclaimed.

If anything here still feels unclear, ask before moving to Lesson 20.
