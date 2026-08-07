"""
Lesson 3: redis-py's Redis.from_url(), and decode_responses, up close.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Redis is running first):

    docker compose up -d redis
    uv run python lessons/redis/01_beginner/03_first_client_connection/lesson.py
"""

import os

import redis
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    dsn = os.environ["REDIS_DSN"]
    print(f"Connecting with DSN: {dsn}")

    # Without decode_responses, every value comes back as bytes.
    raw = redis.Redis.from_url(dsn)
    raw.set("greeting", "hello")
    raw_value = raw.get("greeting")
    print(f"decode_responses=False -> {raw_value!r}")

    # With it, values come back as ordinary Python str.
    r = redis.Redis.from_url(dsn, decode_responses=True)
    decoded_value = r.get("greeting")
    print(f"decode_responses=True  -> {decoded_value!r}")

    r.delete("greeting")


if __name__ == "__main__":
    main()
