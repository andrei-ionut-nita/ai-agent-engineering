"""
Lesson 15: LPUSH/BRPOP, a simple FIFO work queue for worker agents.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Redis is running first):

    docker compose up -d redis
    uv run python lessons/redis/02_intermediate/15_task_queues_with_lists_and_streams/lesson.py
"""

import os

import redis
from dotenv import load_dotenv

load_dotenv()

QUEUE_KEY = "queue:tasks"


def main() -> None:
    dsn = os.environ["REDIS_DSN"]
    r = redis.Redis.from_url(dsn, decode_responses=True)
    r.delete(QUEUE_KEY)

    tasks = [
        "summarize document 42",
        "extract action items from document 43",
        "translate document 44",
    ]
    for task in tasks:
        r.lpush(QUEUE_KEY, task)
    print(f"Pushed {len(tasks)} tasks onto {QUEUE_KEY}")

    for _ in tasks:
        _, task = r.brpop(QUEUE_KEY, timeout=5)
        print(f"Worker popped: {task}")

    empty_result = r.brpop(QUEUE_KEY, timeout=2)
    print(f"BRPOP on empty queue (2s timeout): {empty_result}")


if __name__ == "__main__":
    main()
