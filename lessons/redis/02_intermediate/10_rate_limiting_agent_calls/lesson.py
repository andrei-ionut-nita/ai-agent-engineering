"""
Lesson 10: a fixed-window rate limiter built from INCR and EXPIRE.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Redis is running first):

    docker compose up -d redis
    uv run python lessons/redis/02_intermediate/10_rate_limiting_agent_calls/lesson.py
"""

import os

import redis
from dotenv import load_dotenv

load_dotenv()

LIMIT = 3
WINDOW_SECONDS = 5


def is_allowed(r: redis.Redis, user_id: str) -> tuple[bool, int]:
    key = f"ratelimit:{user_id}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, WINDOW_SECONDS)
    return count <= LIMIT, count


def main() -> None:
    dsn = os.environ["REDIS_DSN"]
    r = redis.Redis.from_url(dsn, decode_responses=True)

    user_id = "u42"
    r.delete(f"ratelimit:{user_id}")

    for call_number in range(1, 5):
        allowed, count = is_allowed(r, user_id)
        status = "allowed" if allowed else "REJECTED"
        print(f"Call {call_number}: {status} (count={count}/{LIMIT})")

    remaining = r.ttl(f"ratelimit:{user_id}")
    print(f"Seconds until reset: {remaining}")


if __name__ == "__main__":
    main()
