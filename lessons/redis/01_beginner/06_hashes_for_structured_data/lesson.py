"""
Lesson 6: HSET, HGETALL, HGET, and HINCRBY, hashes as small objects.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Redis is running first):

    docker compose up -d redis
    uv run python lessons/redis/01_beginner/06_hashes_for_structured_data/lesson.py
"""

import os

import redis
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    dsn = os.environ["REDIS_DSN"]
    r = redis.Redis.from_url(dsn, decode_responses=True)
    r.delete("session:abc123")

    r.hset(
        "session:abc123",
        mapping={
            "user_id": "u42",
            "started_at": "2026-08-07T10:00:00Z",
            "turn_count": 0,
        },
    )

    session = r.hgetall("session:abc123")
    print(f"HGETALL session:abc123 -> {session}")

    turn_count = r.hget("session:abc123", "turn_count")
    print(f"HGET turn_count        -> {turn_count!r}")

    for _ in range(3):
        new_count = r.hincrby("session:abc123", "turn_count", 1)
    print(f"HINCRBY turn_count x3   -> {new_count}")


if __name__ == "__main__":
    main()
