"""
Lesson 1: what Redis is, and proving the server is alive.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Redis is running first):

    docker compose up -d redis
    uv run python lessons/redis/01_beginner/01_what_is_redis/lesson.py
"""

import os

import redis
from dotenv import load_dotenv

# Reads REDIS_DSN from the project root's .env, the same way pgvector
# reads POSTGRES_DSN.
load_dotenv()


def main() -> None:
    dsn = os.environ["REDIS_DSN"]

    # decode_responses=True makes redis-py hand back Python str instead
    # of bytes, every lesson in this course uses it.
    r = redis.Redis.from_url(dsn, decode_responses=True)

    # The simplest possible round trip: ask the server "are you there".
    alive = r.ping()

    server_info = r.info("server")
    memory_info = r.info("memory")

    print(f"Connected to Redis {server_info['redis_version']}")
    print(f"PING -> {alive}")
    print(f"Used memory: {memory_info['used_memory_human']}")


if __name__ == "__main__":
    main()
