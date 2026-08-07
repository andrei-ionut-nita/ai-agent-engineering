# Lesson 12: Redis as working memory vs. pgvector as long-term memory

## Where we left off

Every lesson so far has been Redis mechanics. This lesson is the one
the course README pointed at from the start: the line between what
belongs in Redis and what belongs in pgvector, drawn explicitly.

## Two different jobs, not competing tools

An agent needs two very different kinds of memory:

- **Working memory**: the last few turns of the current conversation, a
  cached answer, an in-flight rate-limit counter, a session's
  metadata. It only needs to survive the current session, or a short
  while past it, and it needs to be read and written on every turn, in
  well under a millisecond. This is everything Lessons 4-11 built.
- **Long-term memory**: a fact worth keeping past this session, a
  document worth being able to find again by meaning, weeks or years
  later, across every future session, not just this one. That's
  pgvector's job: durable storage, and search by semantic similarity,
  covered in that course's Lessons 1-9.

Redis *can* store data past a session (Lesson 20 covers persistence
options), and pgvector *can* be queried quickly, but reaching for the
wrong one for the wrong job means either paying Postgres's
disk-durability cost for state that's thrown away in minutes, or
losing an agent's accumulated knowledge the moment a Redis container
restarts.

## The same agent, using both

```python
# Working memory: this conversation's last few turns, Redis, TTL'd.
r.rpush(f"session:{session_id}:messages", message)
r.expire(f"session:{session_id}:messages", 3600)

# Long-term memory: a fact worth keeping, pgvector, no expiry.
cur.execute(
    "INSERT INTO notes (content, embedding) VALUES (%s, %s)",
    (fact_text, embedding),
)
```

Neither line replaces the other, a real agent writes to both, for
different reasons, on different timescales. Lesson 24's capstone (in
this course) uses Redis for exactly the working-memory half; pgvector's
own capstone (`lessons/pgvector/03_advanced/28_advanced_capstone_project`)
is what the long-term half looks like in full.

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/02_intermediate/12_short_term_vs_long_term_memory/lesson.py
```

The pgvector side is shown as reference code, not executed here, it
needs that course's own Postgres service and DSN, a separate course.

## A rule of thumb

Ask one question: if the process restarts right now, should this
survive? "No, and it's fine if it doesn't" points at Redis. "Yes, an
agent should still know this next week" points at pgvector. Everything
this course has built so far, sessions, caches, rate-limit counters,
answers "no" to that question, that's the whole reason it's ephemeral
by design, not by accident.

## Checkpoint

- **working memory**: short-lived, read/written every turn, fine to
  lose on restart, Redis's job.
- **long-term memory**: durable, searched by meaning across sessions,
  pgvector's job.
- **the test**: "should this survive a restart?" decides which one a
  given piece of state belongs in.

If anything here still feels unclear, ask before moving to Lesson 13.
