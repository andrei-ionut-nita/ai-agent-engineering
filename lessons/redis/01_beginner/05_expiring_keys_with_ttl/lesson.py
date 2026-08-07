"""
Lesson 5: SETEX, EXPIRE, and TTL, expiring keys automatically.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Redis is running first):

    docker compose up -d redis
    uv run python lessons/redis/01_beginner/05_expiring_keys_with_ttl/lesson.py
"""

import os
import time

import redis
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    dsn = os.environ["REDIS_DSN"]
    r = redis.Redis.from_url(dsn, decode_responses=True)
    r.delete("cache:capital_of_france", "session:abc123")

    r.setex("cache:capital_of_france", 60, "Paris")
    print("SETEX cache:capital_of_france 60 'Paris'")
    print(f"TTL right after SETEX: {r.ttl('cache:capital_of_france')}")
    print(f"GET before expiry: {r.get('cache:capital_of_france')!r}")

    r.set("session:abc123", "active")
    r.expire("session:abc123", 1)
    print(f"TTL after EXPIRE 1: {r.ttl('session:abc123')}")

    time.sleep(1.5)
    print(f"GET after 1.5s sleep: {r.get('session:abc123')!r}")


if __name__ == "__main__":
    main()
