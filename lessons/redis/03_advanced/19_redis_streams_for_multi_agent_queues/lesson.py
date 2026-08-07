"""
Lesson 19: streams and consumer groups, durable task handoff.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Redis is running first):

    docker compose up -d redis
    uv run python lessons/redis/03_advanced/19_redis_streams_for_multi_agent_queues/lesson.py
"""

import os

import redis
from dotenv import load_dotenv

load_dotenv()

STREAM_KEY = "stream:tasks"
GROUP_NAME = "workers"


def main() -> None:
    dsn = os.environ["REDIS_DSN"]
    r = redis.Redis.from_url(dsn, decode_responses=True)

    r.delete(STREAM_KEY)

    r.xadd(STREAM_KEY, {"task": "summarize document 42", "priority": "high"})
    r.xadd(STREAM_KEY, {"task": "translate document 43", "priority": "low"})
    print(f"Added 2 tasks to {STREAM_KEY}")

    r.xgroup_create(STREAM_KEY, GROUP_NAME, id="0")

    entries = r.xreadgroup(GROUP_NAME, "worker-1", {STREAM_KEY: ">"}, count=1)
    entry_id, fields = entries[0][1][0]
    print(f"worker-1 read: {fields['task']}")

    pending = r.xpending(STREAM_KEY, GROUP_NAME)
    print(f"Pending before ack: {pending}")

    r.xack(STREAM_KEY, GROUP_NAME, entry_id)
    print(f"worker-1 acked {fields['task']}")

    pending = r.xpending(STREAM_KEY, GROUP_NAME)
    print(f"Pending after ack: {pending}")

    entries = r.xreadgroup(GROUP_NAME, "worker-2", {STREAM_KEY: ">"}, count=1)
    _, fields = entries[0][1][0]
    print(f"worker-2 read: {fields['task']}")


if __name__ == "__main__":
    main()
