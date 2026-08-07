"""
Lesson 7: RPUSH, LRANGE, LTRIM, and LLEN, lists as a message log.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Redis is running first):

    docker compose up -d redis
    uv run python lessons/redis/01_beginner/07_lists_for_conversation_history/lesson.py
"""

import os

import redis
from dotenv import load_dotenv

load_dotenv()

KEY = "session:abc123:messages"


def main() -> None:
    dsn = os.environ["REDIS_DSN"]
    r = redis.Redis.from_url(dsn, decode_responses=True)
    r.delete(KEY)

    messages = [
        "user: what's the weather in Paris?",
        "assistant: 18C and partly cloudy.",
        "user: and tomorrow?",
        "assistant: 20C, mostly sunny.",
    ]
    for message in messages:
        r.rpush(KEY, message)

    print(f"LLEN                -> {r.llen(KEY)}")
    print(f"LRANGE 0 -1 (all)   -> {r.lrange(KEY, 0, -1)}")
    print(f"LRANGE -2 -1 (last) -> {r.lrange(KEY, -2, -1)}")

    r.ltrim(KEY, -2, -1)
    print(f"After LTRIM -2 -1   -> {r.lrange(KEY, 0, -1)}")


if __name__ == "__main__":
    main()
