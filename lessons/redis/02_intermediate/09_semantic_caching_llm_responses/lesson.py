"""
Lesson 9: caching an expensive call by an exact hash of its prompt.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Redis is running first):

    docker compose up -d redis
    uv run python lessons/redis/02_intermediate/09_semantic_caching_llm_responses/lesson.py
"""

import hashlib
import os
import time

import redis
from dotenv import load_dotenv

load_dotenv()

CACHE_TTL_SECONDS = 60


def expensive_llm_call(prompt: str) -> str:
    # Stands in for a real network round trip to an LLM, this course
    # keeps every lesson runnable with no API key.
    time.sleep(1.5)
    return f"Answer to: {prompt}"


def cache_key(prompt: str) -> str:
    digest = hashlib.sha256(prompt.encode()).hexdigest()
    return f"cache:llm:{digest}"


def cached_call(r: redis.Redis, prompt: str) -> tuple[str, bool]:
    key = cache_key(prompt)
    cached = r.get(key)
    if cached is not None:
        return cached, True

    answer = expensive_llm_call(prompt)
    r.setex(key, CACHE_TTL_SECONDS, answer)
    return answer, False


def main() -> None:
    dsn = os.environ["REDIS_DSN"]
    r = redis.Redis.from_url(dsn, decode_responses=True)

    prompts = [
        "What is the capital of France?",
        "What is the capital of France?",
        "What is the capital of Germany?",
    ]
    for prompt in prompts:
        r.delete(cache_key(prompt))

    for prompt in prompts:
        start = time.monotonic()
        _, was_cached = cached_call(r, prompt)
        elapsed = time.monotonic() - start
        status = "HIT" if was_cached else "MISS"
        print(f"Call ({prompt}): {status}, took {elapsed:.1f}s")


if __name__ == "__main__":
    main()
