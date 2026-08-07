"""
Lesson 20: RDB snapshots vs. AOF logging, reading the tradeoff back
from the server's own config and INFO output.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Redis is running first):

    docker compose up -d redis
    uv run python lessons/redis/03_advanced/20_persistence_rdb_vs_aof/lesson.py
"""

import os

import redis
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    dsn = os.environ["REDIS_DSN"]
    r = redis.Redis.from_url(dsn, decode_responses=True)

    save_policy = r.config_get("save")["save"]
    appendonly = r.config_get("appendonly")["appendonly"]
    print(f"save policy: {save_policy}")
    print(f"appendonly:  {appendonly}")

    r.bgsave()
    print("BGSAVE triggered")

    info = r.info("persistence")
    print(f"rdb_last_bgsave_status: {info['rdb_last_bgsave_status']}")
    print(f"aof_enabled: {info['aof_enabled']}")


if __name__ == "__main__":
    main()
