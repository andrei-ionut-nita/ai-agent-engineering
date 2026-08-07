"""
Lesson 11: PUBLISH/SUBSCRIBE, streaming an agent's progress live.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Redis is running first):

    docker compose up -d redis
    uv run python lessons/redis/02_intermediate/11_pub_sub_for_streaming_events/lesson.py
"""

import os
import threading
import time

import redis
from dotenv import load_dotenv

load_dotenv()

CHANNEL = "agent:progress"
EVENTS = [
    "searching for relevant documents...",
    "found 3 candidates, reading the top one...",
    "drafting an answer...",
    "done",
]


def run_publisher(r: redis.Redis) -> None:
    # A short pause lets the subscriber's own SUBSCRIBE confirmation
    # print first, so the output reads top to bottom in order.
    time.sleep(0.3)
    for event in EVENTS:
        r.publish(CHANNEL, event)
        time.sleep(0.2)


def main() -> None:
    dsn = os.environ["REDIS_DSN"]
    r = redis.Redis.from_url(dsn, decode_responses=True)

    pubsub = r.pubsub()
    pubsub.subscribe(CHANNEL)

    publisher_thread = threading.Thread(target=run_publisher, args=(r,))
    publisher_thread.start()

    received = 0
    for item in pubsub.listen():
        if item["type"] == "subscribe":
            print(f"Subscribed to {CHANNEL}")
            continue
        if item["type"] == "message":
            print(f"Received: {item['data']}")
            received += 1
            if received == len(EVENTS):
                break

    publisher_thread.join()
    pubsub.close()


if __name__ == "__main__":
    main()
