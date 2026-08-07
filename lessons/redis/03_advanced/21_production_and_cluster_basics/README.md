# Lesson 21: Replication, sharding, and when a single node stops being enough

## Where we left off

Every lesson so far has run against one container, one process, one
copy of the data. That's fine for learning, and fine for a lot of real
workloads too, but it's worth knowing what changes once "one Redis"
stops being enough, in either direction: reliability, or size.

## Replication: copies for reliability, not capacity

A **replica** is a second Redis instance that continuously receives a
copy of everything the primary writes. If the primary goes down, a
replica (promoted to primary, manually or via Sentinel/Cluster's
automatic failover) can take over with the data intact, up to
whatever replication lag existed at the moment of failure. Replication
solves "what if this one process dies", it does *not* solve "this one
process is out of RAM", every replica holds the *same* full dataset,
not a share of it.

```python
info = r.info("replication")
info["connected_slaves"]   # 0 in this course's single-node setup
info["role"]               # "master"
```

This course's container reports `connected_slaves: 0` and `role:
master`, an honest single-node dev setup, no replicas configured.
Reading these fields is how you'd confirm replication is actually
working on a real deployment, not just assume it from a config file.

## Sharding: splitting data across nodes for capacity

**Sharding** (Redis Cluster's own term) is the other axis: instead of
every node holding everything, the keyspace is split into 16384 fixed
**hash slots**, each node owns a range of them, and a key's slot is
computed from a hash of the key itself (`CRC16(key) % 16384`). A
cluster of, say, 3 primaries each hold roughly a third of the data,
letting total capacity and throughput grow with the number of nodes,
something replication alone can't do.

```bash
docker compose exec redis redis-cli -a redis CLUSTER INFO
# ERR This instance has cluster support disabled
```

This course's container isn't running in cluster mode (`cluster_enabled: 0` inside `CLUSTER INFO`, or the error above for a plain single-node instance), the exact command this course's compose file would need to add is `--cluster-enabled yes` on multiple coordinating instances, genuinely out of scope for a local Docker Compose learning setup, but worth knowing exists once a real dataset outgrows one node's memory.

## Multi-key commands and cluster mode

One practical consequence worth knowing ahead of time: in cluster
mode, a command touching multiple keys (a `MGET`, a Lua script over
several keys) only works if every key involved hashes to the *same*
slot, otherwise it errors. Redis supports `{hashtag}` key naming
(`session:{abc123}:messages` and `session:{abc123}:meta` both hash on
`abc123`) specifically so related keys can be forced onto the same
slot, worth knowing the pattern exists, even without a cluster running
here to demonstrate it against.

## When each is worth reaching for

- **Replication**: as soon as an outage losing all of Redis's state is
  a real problem, independent of how much data there is.
- **Sharding**: once the dataset (or the write throughput) outgrows
  what one node's memory or CPU can hold, independent of reliability
  concerns.
- **Both together**: Redis Cluster's normal production shape, sharded
  primaries, each with its own replica(s).

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/03_advanced/21_production_and_cluster_basics/lesson.py
```

## Expected output

```
role: master
connected_slaves: 0
CLUSTER INFO: cluster support disabled on this single-node instance (This instance has cluster support disabled)
```

## Checkpoint

- **replication**: full copies for reliability (survive a node dying),
  every replica holds the whole dataset, doesn't add capacity.
- **sharding**: 16384 hash slots split across nodes, adds capacity and
  throughput, is what Redis Cluster actually shards on.
- **`{hashtag}` keys**: force related keys onto the same cluster slot
  so multi-key commands over them still work.

If anything here still feels unclear, ask before moving to Lesson 22.
