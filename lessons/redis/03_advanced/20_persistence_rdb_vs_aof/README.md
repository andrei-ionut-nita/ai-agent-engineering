# Lesson 20: Snapshotting vs. append-only logging, durability tradeoffs

## Where we left off

Lesson 1 was upfront: Redis is in-memory, and loses its contents if
the process dies, by default. "By default" was doing real work in that
sentence, Redis has two optional persistence mechanisms, and this
course's own container has one of them (RDB) on and the other (AOF)
off. This lesson is about what that choice actually trades away.

## RDB: periodic snapshots

```bash
docker compose exec redis redis-cli -a redis CONFIG GET save
# "3600 1 300 100 60 10000"
```

RDB (Redis Database) periodically writes the *entire* dataset to a
single compact file on disk. The `save` config above means "snapshot
if at least 1 key changed in 3600 seconds, OR at least 100 changed in
300 seconds, OR at least 10000 changed in 60 seconds", Redis's own
compose image ships with this default. A snapshot is fast to load on
restart (one file, read straight into memory) but loses everything
written *since* the last snapshot if the process crashes between them,
up to the whole interval's worth of writes, in the worst case.

## Triggering a snapshot manually

```python
r.bgsave()
```

`BGSAVE` forks a background process to write a snapshot without
blocking the main server (`SAVE`, without the `BG`, exists too, but
blocks every other command until it finishes, essentially never what
you want).

## AOF: every write, logged

```bash
docker compose exec redis redis-cli -a redis CONFIG GET appendonly
# "no", off by default in this course's container
```

AOF (Append-Only File) logs every write command as it happens, instead
of snapshotting state periodically. `appendfsync everysec` (the
default when AOF is on) means the log is flushed to disk roughly once
a second, so a crash loses at most about a second of writes, not a
whole snapshot interval. The cost: a growing log file (Redis
periodically rewrites/compacts it in the background) and a slower
restart, replaying the log instead of loading one snapshot file.

## Reading the tradeoff back from `INFO persistence`

```python
info = r.info("persistence")
info["rdb_last_bgsave_status"]  # "ok" if the last snapshot succeeded
info["aof_enabled"]             # 0 or 1
```

This is the same instinct as Lesson 23's `INFO memory`, ask the
running server what it's actually configured and doing, rather than
assuming from the compose file alone.

## Why this course's default (RDB only) is a reasonable choice

Everything this course has built, sessions, caches, rate limits, is
working memory by design (Lesson 12), losing a few seconds of it on a
crash is rarely a real problem, it'll be rebuilt on the next call
anyway. A system storing something that must never be lost between
snapshots (a payment state machine, an irreplaceable event) would turn
AOF on too, that's a one-line `CONFIG SET appendonly yes`, not a
different database.

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/03_advanced/20_persistence_rdb_vs_aof/lesson.py
```

## Expected output

```
save policy: 3600 1 300 100 60 10000
appendonly:  no
BGSAVE triggered
rdb_last_bgsave_status: ok
aof_enabled: 0
```

## Checkpoint

- **RDB**: periodic full snapshots, fast restart, can lose everything
  since the last snapshot on a crash.
- **AOF**: every write logged, roughly a second of loss on crash
  (`appendfsync everysec`), slower restart, a growing log file.
- **the tradeoff is configurable, not fixed**: `CONFIG SET appendonly
  yes` turns AOF on for data that can't tolerate RDB's window.

If anything here still feels unclear, ask before moving to Lesson 21.
