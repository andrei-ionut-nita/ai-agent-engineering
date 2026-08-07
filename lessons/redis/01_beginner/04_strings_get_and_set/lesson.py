"""
Lesson 4: SET, GET, and INCR, the basic string type.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Redis is running first):

    docker compose up -d redis
    uv run python lessons/redis/01_beginner/04_strings_get_and_set/lesson.py
"""

import os

import redis
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    dsn = os.environ["REDIS_DSN"]
    r = redis.Redis.from_url(dsn, decode_responses=True)
    r.delete("agent:last_response", "agent:call_count", "agent:missing_key")

    r.set("agent:last_response", "The weather in Paris is 18C.")
    print(f"GET agent:last_response -> {r.get('agent:last_response')!r}")

    print(f"GET agent:missing_key   -> {r.get('agent:missing_key')!r}")

    r.set("agent:call_count", 0)
    for _ in range(3):
        new_count = r.incr("agent:call_count")
    print(f"INCR agent:call_count x3 -> {new_count}")

    r.set("agent:last_response", "Updated answer.")
    print(f"GET after overwrite      -> {r.get('agent:last_response')!r}")


if __name__ == "__main__":
    main()
