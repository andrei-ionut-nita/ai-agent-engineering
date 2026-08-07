# Lesson 8: Beginner Checkpoint - Chatbot with Redis-Backed Session Memory

## What this is

No new concepts in this lesson. This is a checkpoint: a small, real
script built entirely out of ideas from Lessons 1 through 7, combined
into one thing. If you can read `lesson.py` and understand why every
piece is there, you've mastered the Beginner tier. If any piece feels
unfamiliar, that's a sign to revisit the lesson it came from before
continuing to Intermediate.

## What it does

Simulates a short chat session for one user: creates a session hash
with metadata, appends each turn to a message-history list, bumps the
session's turn count on every message, keeps the history capped at a
bounded size, and gives the whole session a TTL so an abandoned
conversation cleans itself up instead of living forever. It prints the
session's state after each turn so you can see it accumulate.

## Where each piece came from

```python
r.hset(f"session:{session_id}", mapping={"user_id": ..., "started_at": ..., "turn_count": 0})
r.expire(f"session:{session_id}", SESSION_TTL_SECONDS)
```
Lesson 6 (a hash for session metadata) and Lesson 5 (`EXPIRE`, giving
the whole session a lifespan).

```python
r.rpush(f"session:{session_id}:messages", message)
r.ltrim(f"session:{session_id}:messages", -MAX_HISTORY, -1)
```
Lesson 7 (`RPUSH` to append, `LTRIM` to keep the history bounded).

```python
r.hincrby(f"session:{session_id}", "turn_count", 1)
```
Lesson 6 (`HINCRBY`, updating one field of the session hash without
touching the rest).

```python
r.expire(f"session:{session_id}:messages", SESSION_TTL_SECONDS)
```
Lesson 5 again, this time on the message list: both keys belonging to
one session get the same TTL, so the whole session expires together,
not just its metadata.

```python
r.hgetall(f"session:{session_id}")
r.lrange(f"session:{session_id}:messages", 0, -1)
```
Lesson 6 and Lesson 7's read sides, used here to print the session's
state after each turn.

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/01_beginner/08_beginner_checkpoint_project/lesson.py
```

You should see: a new session created with `turn_count` at `0`, each
simulated turn increasing `turn_count` by one and appending two lines
to the message history (user, then assistant), the history staying
capped at `MAX_HISTORY` entries even after more turns than that have
happened, and a TTL present on both keys the whole time.

## Try this yourself

Without looking anything up:

- Lower `MAX_HISTORY` to `2` and rerun, confirm the printed history
  after the last turn only ever shows the most recent exchange.
- Lower `SESSION_TTL_SECONDS` to `2`, add a short `time.sleep(3)` before
  the final read, and confirm both keys have expired (`HGETALL`
  returns `{}`, `LRANGE` returns `[]`).
- Add a second, independent session with a different `session_id` and
  confirm its keys and TTL are entirely separate from the first.

If you can make these changes confidently, you're ready for the
Intermediate tier, starting at Lesson 9.
