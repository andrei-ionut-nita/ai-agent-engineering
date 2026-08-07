# Lesson 23: `INFO`, eviction policies, what happens when Redis runs out of RAM

## Where we left off

Redis being in-memory (Lesson 1) means it's also memory-*bounded*: RAM
isn't infinite the way disk mostly feels like it is. This lesson is
about what Redis does at that boundary, and how to watch it coming
before it arrives.

## `INFO memory`: what's actually being used

```python
info = r.info("memory")
info["used_memory_human"]   # e.g. "3.83M"
info["maxmemory_human"]     # "0B" means unlimited, this course's default
info["maxmemory_policy"]    # what happens once maxmemory is hit
```

`INFO` (already used in Lessons 1, 20, and 21, for different sections)
is the same idea here: ask the running server, don't guess from
config alone. `maxmemory: 0` means no cap is set, this course's
container will simply keep growing until the host machine itself runs
out, a deliberate default for local learning, not a production
setting.

## Setting a cap

```python
r.config_set("maxmemory", "100mb")
r.config_set("maxmemory-policy", "allkeys-lru")
```

`maxmemory` sets the cap; `maxmemory-policy` decides what happens once
it's reached, since without eviction, Redis would just start rejecting
writes.

## The eviction policies that matter for an agent's cache

- **`noeviction`** (the default): reject writes with an error once
  full, nothing is deleted automatically. Right for data you'd rather
  fail loudly on than silently lose, wrong for a cache.
- **`allkeys-lru`**: evicts the *least recently used* key, of any key,
  regardless of whether it has a TTL. A reasonable default for a pure
  cache where every key is disposable.
- **`volatile-lru`**: evicts the least recently used key *among keys
  that have a TTL set*, keys with no TTL are never evicted this way.
  The right policy when some keys (session data, meant to expire on
  its own) share a Redis instance with keys that must never be
  silently dropped (nothing without a TTL will be).
- **`volatile-ttl`**: evicts the key with the *soonest* expiry among
  TTL'd keys first, rather than by recency of use, prioritizing "this
  was going to disappear soon anyway".

Everything this course has built (sessions, caches, rate-limit
counters) is TTL'd, working memory by design (Lesson 12), which makes
`volatile-lru` or `volatile-ttl` the natural choices for a real
deployment: evict expendable, expiring data under pressure, never
something that was set to live forever on purpose.

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/03_advanced/23_monitoring_and_memory_eviction/lesson.py
```

## Expected output

```
used_memory: 3.8...M
maxmemory: 0B (0 = unlimited, this course's default)
maxmemory_policy: noeviction
After CONFIG SET: maxmemory=104857600, policy=allkeys-lru
Reverted to unlimited/noeviction for the rest of this course
```

## Checkpoint

- **`INFO memory`**: the running server's actual memory usage and
  eviction configuration, not just what a config file claims.
- **`maxmemory-policy`**: `noeviction` fails writes once full,
  `allkeys-*`/`volatile-*` variants pick what to evict instead.
- **for this course's data**: `volatile-lru`/`volatile-ttl` fit best,
  everything built so far already carries a TTL.

If anything here still feels unclear, ask before moving to Lesson 24.
