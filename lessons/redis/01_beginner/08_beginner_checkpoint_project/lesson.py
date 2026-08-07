"""
Lesson 8: Beginner Checkpoint - Chatbot with Redis-Backed Session Memory.

No new concepts, this combines Lessons 1-7 into one small script.
Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Redis is running first):

    docker compose up -d redis
    uv run python lessons/redis/01_beginner/08_beginner_checkpoint_project/lesson.py
"""

import os
from datetime import UTC, datetime

import redis
from dotenv import load_dotenv

load_dotenv()

MAX_HISTORY = 6
SESSION_TTL_SECONDS = 300

TURNS = [
    ("user", "what's the weather in Paris?"),
    ("assistant", "18C and partly cloudy."),
    ("user", "and tomorrow?"),
    ("assistant", "20C, mostly sunny."),
    ("user", "should I bring an umbrella either day?"),
    ("assistant", "no, both days look dry."),
]


def session_key(session_id: str) -> str:
    return f"session:{session_id}"


def messages_key(session_id: str) -> str:
    return f"session:{session_id}:messages"


def start_session(r: redis.Redis, session_id: str, user_id: str) -> None:
    r.hset(
        session_key(session_id),
        mapping={
            "user_id": user_id,
            "started_at": datetime.now(UTC).isoformat(),
            "turn_count": 0,
        },
    )
    r.expire(session_key(session_id), SESSION_TTL_SECONDS)


def add_turn(r: redis.Redis, session_id: str, role: str, text: str) -> None:
    message = f"{role}: {text}"
    r.rpush(messages_key(session_id), message)
    r.ltrim(messages_key(session_id), -MAX_HISTORY, -1)
    r.expire(messages_key(session_id), SESSION_TTL_SECONDS)
    r.hincrby(session_key(session_id), "turn_count", 1)


def print_session_state(r: redis.Redis, session_id: str) -> None:
    metadata = r.hgetall(session_key(session_id))
    history = r.lrange(messages_key(session_id), 0, -1)
    print(f"  turn_count={metadata.get('turn_count')} history={history}")


def main() -> None:
    dsn = os.environ["REDIS_DSN"]
    r = redis.Redis.from_url(dsn, decode_responses=True)

    session_id = "abc123"
    r.delete(session_key(session_id), messages_key(session_id))

    start_session(r, session_id, user_id="u42")
    print(f"Started session {session_id}")
    print_session_state(r, session_id)

    for role, text in TURNS:
        add_turn(r, session_id, role, text)
        print(f"After turn ({role}): {text!r}")
        print_session_state(r, session_id)


if __name__ == "__main__":
    main()
