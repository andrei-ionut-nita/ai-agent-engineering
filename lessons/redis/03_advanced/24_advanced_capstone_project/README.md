# Lesson 24: Capstone - A Multi-Agent System Using Redis for Memory, Queue, and Cache

## What this is

No new concepts in this lesson. This is the capstone: a small,
realistic two-agent pipeline built entirely out of ideas from every
tier of this course, combined into one thing. If you can read
`lesson.py` and understand why every piece is there, you've completed
the course.

## What it does

A **coordinator** agent receives a batch of user questions for one
session. For each question, it appends the question to the session's
message history (memory), then hands the question off as a task on a
Redis stream (queue) instead of answering it directly. A **worker**
agent, running independently against the same stream, reads tasks
through a consumer group, checks a prompt-hash cache before doing any
real work, runs the (simulated) expensive call on a miss, appends the
answer back to the same session's message history, and acknowledges
the task. The script prints each step so you can see memory, queue,
and cache all doing their own separate job for the same conversation.

## Where each piece came from

```python
r.rpush(f"session:{session_id}:messages", f"user: {question}")
r.ltrim(f"session:{session_id}:messages", -MAX_HISTORY, -1)
```
Lessons 7-8 (bounded conversation history), the **memory** piece, used
by both agents to read and write the same session.

```python
r.xadd(QUEUE_STREAM, {"session_id": session_id, "question": question})
```
Lesson 19 (streams as a durable handoff), the **queue** piece: the
coordinator doesn't process the question itself, it hands it off.

```python
r.xgroup_create(QUEUE_STREAM, GROUP_NAME, id="0")
entries = r.xreadgroup(GROUP_NAME, "worker-1", {QUEUE_STREAM: ">"}, count=1)
...
r.xack(QUEUE_STREAM, GROUP_NAME, entry_id)
```
Lesson 19 again, the worker's side: read as part of a consumer group,
acknowledge once done, so a crashed worker wouldn't silently drop a
question.

```python
key = f"cache:llm:{hashlib.sha256(question.encode()).hexdigest()}"
cached = r.get(key)
...
r.setex(key, CACHE_TTL_SECONDS, answer)
```
Lesson 9 (cache by prompt hash), the **cache** piece, checked by the
worker before running the expensive call.

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/03_advanced/24_advanced_capstone_project/lesson.py
```

You should see: the coordinator enqueueing all three questions first,
without waiting on the worker at all (the whole point of a queue,
Lesson 15/19), then the worker processing them in order (a `MISS` the
first time a question is asked, a `HIT` for the repeated one). The
final session history reflects that same decoupling: all three `user:`
entries first (written by the coordinator, up front), then all three
`assistant:` entries (written by the worker, after), not interleaved
turn by turn the way Lesson 8's single-agent chatbot was.

## Try this yourself

- Add a second worker (`worker-2`, its own `xreadgroup` call) and split
  the batch of questions between the two workers running in a loop,
  confirm the consumer group hands each task to exactly one of them
  (Lesson 19's guarantee).
- Add the rate limiter from Lesson 10 in front of the coordinator's
  enqueue step, and confirm a question over the limit never reaches the
  stream at all.
- Add the `agent:progress` channel from Lesson 11, published by the
  worker before and after each task, and print it from a third,
  independent subscriber running alongside the coordinator and worker.

This is the last lesson in the course, if you can make these changes
confidently, revisit Lesson 12: with both halves of an agent's memory
now built (this course's working memory, pgvector's long-term memory),
that lesson's distinction should feel concrete rather than abstract.
