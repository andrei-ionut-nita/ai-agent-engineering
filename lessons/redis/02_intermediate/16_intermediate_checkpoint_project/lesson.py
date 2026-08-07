"""
Lesson 16: Intermediate Checkpoint - Cached, Rate-Limited, Streaming
Chatbot.

No new concepts, this combines Lessons 7-11 into one small script.
Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Redis is running first):

    docker compose up -d redis
    uv run python lessons/redis/02_intermediate/16_intermediate_checkpoint_project/lesson.py
"""

import hashlib
import os
import threading
import time

import redis
from dotenv import load_dotenv

load_dotenv()

SESSION_ID = "abc123"
USER_ID = "u42"
CACHE_TTL_SECONDS = 60
MAX_HISTORY = 10
RATE_LIMIT_MAX_CALLS = 3
RATE_LIMIT_WINDOW_SECONDS = 30
PROGRESS_CHANNEL = "agent:progress"

MESSAGES = [
    "what's the weather in Paris?",
    "what's the weather in Berlin?",
    "what's the weather in Paris?",  # repeats message 1: should be a cache HIT
    "what's the weather in Madrid?",
    "what's the weather in Lisbon?",  # exceeds RATE_LIMIT_MAX_CALLS
]


def expensive_llm_call(prompt: str) -> str:
    time.sleep(0.5)
    return f"Answer to: {prompt}"


def cache_key(prompt: str) -> str:
    digest = hashlib.sha256(prompt.encode()).hexdigest()
    return f"cache:llm:{digest}"


def run_subscriber(r: redis.Redis, expected: int) -> None:
    pubsub = r.pubsub()
    pubsub.subscribe(PROGRESS_CHANNEL)
    received = 0
    for item in pubsub.listen():
        if item["type"] != "message":
            continue
        print(f"  [progress] {item['data']}")
        received += 1
        if received == expected:
            break
    pubsub.close()


def handle_message(r: redis.Redis, prompt: str) -> None:
    count = r.incr(f"ratelimit:{USER_ID}")
    if count == 1:
        r.expire(f"ratelimit:{USER_ID}", RATE_LIMIT_WINDOW_SECONDS)
    if count > RATE_LIMIT_MAX_CALLS:
        print(f"REJECTED (rate limit): {prompt!r}")
        return

    r.publish(PROGRESS_CHANNEL, f"handling: {prompt}")

    key = cache_key(prompt)
    cached = r.get(key)
    if cached is not None:
        answer, was_cached = cached, True
    else:
        answer = expensive_llm_call(prompt)
        r.setex(key, CACHE_TTL_SECONDS, answer)
        was_cached = False

    status = "HIT" if was_cached else "MISS"
    print(f"[{status}] {prompt!r} -> {answer!r}")

    messages_key = f"session:{SESSION_ID}:messages"
    r.rpush(messages_key, f"user: {prompt}")
    r.rpush(messages_key, f"assistant: {answer}")
    r.ltrim(messages_key, -MAX_HISTORY, -1)


def main() -> None:
    dsn = os.environ["REDIS_DSN"]
    r = redis.Redis.from_url(dsn, decode_responses=True)

    r.delete(
        f"ratelimit:{USER_ID}",
        f"session:{SESSION_ID}:messages",
        *(cache_key(m) for m in MESSAGES),
    )

    expected_progress_events = min(RATE_LIMIT_MAX_CALLS, len(MESSAGES))
    subscriber_thread = threading.Thread(
        target=run_subscriber, args=(r, expected_progress_events)
    )
    subscriber_thread.start()
    time.sleep(0.3)  # let the subscriber's SUBSCRIBE land first

    for prompt in MESSAGES:
        handle_message(r, prompt)

    subscriber_thread.join()

    history = r.lrange(f"session:{SESSION_ID}:messages", 0, -1)
    print(f"\nFinal session history: {history}")


if __name__ == "__main__":
    main()
