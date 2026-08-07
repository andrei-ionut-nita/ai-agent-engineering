# Lesson 15: A simple work queue for handing tasks to worker agents

## Where we left off

Lesson 7 used `RPUSH` to append to a list and read it with `LRANGE`.
This lesson uses the *other* end of a list, and a blocking read, to
turn that same value type into a work queue: one process hands off
tasks, another (or several) picks them up and processes them.

## Producer: `LPUSH` onto the queue

```python
r.lpush("queue:tasks", "summarize document 42")
```

Pushing to the **left** (head) end while reading from the right
(tail) makes this a FIFO queue: the first task pushed is the first one
a worker sees, first in, first out, same order it arrived in.

## Worker: `BRPOP`, a blocking pop

```python
result = r.brpop("queue:tasks", timeout=5)
```

`BRPOP key timeout` pops from the tail if something's there
*immediately*; if the queue is empty, it blocks the calling process,
waiting up to `timeout` seconds for something to arrive, rather than
the worker polling in a `while True: sleep(0.1)` loop burning CPU on
mostly-empty checks. It returns `None` on timeout, or a `(key, value)`
tuple once something's popped.

## One task, one worker: no double-processing

`BRPOP` (and `RPOP`) removes the item from the list as part of the same
atomic call that returns it, two workers calling `BRPOP` on the same
queue at the same time can't both receive the same task, Redis hands
each waiting worker a different item as they arrive. This is the
property that makes a Redis list a real queue and not just a shared
list both workers happen to read.

## The limit of this approach

If a worker pops a task and then crashes before finishing it, that
task is simply gone, `BRPOP` already removed it, nothing remembers it
was ever handed out. That's an acceptable tradeoff for low-stakes,
retryable work, but not for a task that absolutely must be completed
once picked up. Lesson 19's consumer groups solve exactly this: a
durable queue that tracks which messages have been acknowledged and
lets an unacknowledged one be claimed by another worker.

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/02_intermediate/15_task_queues_with_lists_and_streams/lesson.py
```

## Expected output

```
Pushed 3 tasks onto queue:tasks
Worker popped: summarize document 42
Worker popped: extract action items from document 43
Worker popped: translate document 44
BRPOP on empty queue (2s timeout): None
```

## Checkpoint

- **`LPUSH`/`BRPOP`**: push to the head, pop from the tail, a FIFO
  queue built from a list.
- **`BRPOP`'s blocking wait**: a worker waits up to `timeout` seconds
  for work, instead of polling in a loop.
- **the limit**: a popped-but-uncompleted task is simply lost, no
  acknowledgment tracking, Lesson 19's streams add that.

If anything here still feels unclear, ask before moving to Lesson 16.
