"""
Lesson 24: Capstone - A Multi-Agent System Using Redis for Memory,
Queue, and Cache.

No new concepts, this combines Lessons 7-9 and 19 into one small
two-agent pipeline. Read README.md in this folder first, then read
this file top to bottom, then run it with (make sure Redis is
running first):

    docker compose up -d redis
    uv run python lessons/redis/03_advanced/24_advanced_capstone_project/lesson.py
"""

import hashlib
import os
import time

import redis
from dotenv import load_dotenv

load_dotenv()

SESSION_ID = "abc123"
MAX_HISTORY = 20
QUEUE_STREAM = "stream:agent_tasks"
GROUP_NAME = "workers"
CACHE_TTL_SECONDS = 60

QUESTIONS = [
    "what's the weather in Paris?",
    "what's the weather in Berlin?",
    "what's the weather in Paris?",  # repeats question 1: should be a cache HIT
]


def messages_key(session_id: str) -> str:
    return f"session:{session_id}:messages"


def cache_key(question: str) -> str:
    digest = hashlib.sha256(question.encode()).hexdigest()
    return f"cache:llm:{digest}"


def expensive_llm_call(question: str) -> str:
    time.sleep(0.5)
    return f"Answer to: {question}"


def coordinator_enqueue(r: redis.Redis, session_id: str, question: str) -> None:
    r.rpush(messages_key(session_id), f"user: {question}")
    r.ltrim(messages_key(session_id), -MAX_HISTORY, -1)
    r.xadd(QUEUE_STREAM, {"session_id": session_id, "question": question})
    print(f"[coordinator] enqueued: {question!r}")


def worker_process_one(r: redis.Redis, consumer_name: str) -> bool:
    entries = r.xreadgroup(GROUP_NAME, consumer_name, {QUEUE_STREAM: ">"}, count=1)
    if not entries or not entries[0][1]:
        return False

    entry_id, fields = entries[0][1][0]
    session_id = fields["session_id"]
    question = fields["question"]

    key = cache_key(question)
    cached = r.get(key)
    if cached is not None:
        answer, status = cached, "HIT"
    else:
        answer = expensive_llm_call(question)
        r.setex(key, CACHE_TTL_SECONDS, answer)
        status = "MISS"

    r.rpush(messages_key(session_id), f"assistant: {answer}")
    r.ltrim(messages_key(session_id), -MAX_HISTORY, -1)
    r.xack(QUEUE_STREAM, GROUP_NAME, entry_id)

    print(f"[worker]      [{status}] {question!r} -> {answer!r}")
    return True


def main() -> None:
    dsn = os.environ["REDIS_DSN"]
    r = redis.Redis.from_url(dsn, decode_responses=True)

    r.delete(QUEUE_STREAM, messages_key(SESSION_ID), *(cache_key(q) for q in QUESTIONS))
    r.xgroup_create(QUEUE_STREAM, GROUP_NAME, id="0", mkstream=True)

    for question in QUESTIONS:
        coordinator_enqueue(r, SESSION_ID, question)

    for _ in QUESTIONS:
        worker_process_one(r, "worker-1")

    history = r.lrange(messages_key(SESSION_ID), 0, -1)
    print(f"\nFinal session history: {history}")


if __name__ == "__main__":
    main()
