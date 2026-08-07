"""
Lesson 13: RedisJSON, storing and updating nested agent state.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Redis is running first):

    docker compose up -d redis
    uv run python lessons/redis/02_intermediate/13_json_documents_with_redisjson/lesson.py
"""

import os

import redis
from dotenv import load_dotenv

load_dotenv()

KEY = "agent:plan:abc123"


def main() -> None:
    dsn = os.environ["REDIS_DSN"]
    r = redis.Redis.from_url(dsn, decode_responses=True)
    r.delete(KEY)

    r.json().set(
        KEY,
        "$",
        {
            "goal": "research the weather in three cities",
            "steps": [
                {"city": "Paris", "done": True, "retries": 0},
                {"city": "Berlin", "done": False, "retries": 0},
                {"city": "Madrid", "done": False, "retries": 0},
            ],
        },
    )

    print(f"Full document: {r.json().get(KEY)}")
    print(f"Goal only: {r.json().get(KEY, '$.goal')}")

    before = r.json().get(KEY, "$.steps[1].done")[0]
    print(f"Berlin done, before: {before}")

    r.json().set(KEY, "$.steps[1].done", True)
    after = r.json().get(KEY, "$.steps[1].done")[0]
    print(f"Berlin done, after:  {after}")

    retries = r.json().numincrby(KEY, "$.steps[1].retries", 1)
    print(f"Berlin retries after NUMINCRBY: {retries[0]}")


if __name__ == "__main__":
    main()
