"""
Lesson 23: INFO memory, and maxmemory-policy, eviction under pressure.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Redis is running first):

    docker compose up -d redis
    uv run python lessons/redis/03_advanced/23_monitoring_and_memory_eviction/lesson.py
"""

import os

import redis
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    dsn = os.environ["REDIS_DSN"]
    r = redis.Redis.from_url(dsn, decode_responses=True)

    info = r.info("memory")
    print(f"used_memory: {info['used_memory_human']}")
    print(f"maxmemory: {info['maxmemory_human']} (0 = unlimited, this course's default)")
    print(f"maxmemory_policy: {info['maxmemory_policy']}")

    r.config_set("maxmemory", "100mb")
    r.config_set("maxmemory-policy", "allkeys-lru")
    updated = r.info("memory")
    print(
        f"After CONFIG SET: maxmemory={updated['maxmemory']}, "
        f"policy={updated['maxmemory_policy']}"
    )

    # Revert, so later lessons in this course see the same defaults.
    r.config_set("maxmemory", "0")
    r.config_set("maxmemory-policy", "noeviction")
    print("Reverted to unlimited/noeviction for the rest of this course")


if __name__ == "__main__":
    main()
