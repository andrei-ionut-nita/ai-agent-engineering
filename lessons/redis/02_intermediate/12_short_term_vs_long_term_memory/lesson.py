"""
Lesson 12: Redis as working memory vs. pgvector as long-term memory.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Redis is running first):

    docker compose up -d redis
    uv run python lessons/redis/02_intermediate/12_short_term_vs_long_term_memory/lesson.py
"""

import os

import redis
from dotenv import load_dotenv

load_dotenv()

# The long-term half, shown for contrast, not run here: it needs the
# pgvector course's own Postgres service (`docker compose up -d db`)
# and its own DSN, a separate course, a separate database.
PGVECTOR_EXAMPLE = """
cur.execute(
    "INSERT INTO notes (content, embedding) VALUES (%s, %s)",
    (fact_text, embedding),
)
"""


def write_working_memory(r: redis.Redis, session_id: str, message: str) -> None:
    key = f"session:{session_id}:messages"
    r.rpush(key, message)
    r.expire(key, 3600)  # gone in an hour, whether or not it's read again


def main() -> None:
    dsn = os.environ["REDIS_DSN"]
    r = redis.Redis.from_url(dsn, decode_responses=True)

    session_id = "abc123"
    key = f"session:{session_id}:messages"
    r.delete(key)

    write_working_memory(r, session_id, "user: what's the weather in Paris?")
    print(f"Working memory (Redis, TTL={r.ttl(key)}s): {r.lrange(key, 0, -1)}")

    print("\nLong-term memory (pgvector, no expiry) would instead run:")
    print(PGVECTOR_EXAMPLE.strip())
    print(
        "\nSame agent, two stores: this session's messages expire on their "
        "own, a fact worth keeping doesn't."
    )


if __name__ == "__main__":
    main()
