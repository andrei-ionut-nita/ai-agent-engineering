"""
Lesson 21: reading replication status, and confirming this course's
container isn't running in cluster mode.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Redis is running first):

    docker compose up -d redis
    uv run python lessons/redis/03_advanced/21_production_and_cluster_basics/lesson.py
"""

import os

import redis
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    dsn = os.environ["REDIS_DSN"]
    r = redis.Redis.from_url(dsn, decode_responses=True)

    info = r.info("replication")
    print(f"role: {info['role']}")
    print(f"connected_slaves: {info['connected_slaves']}")

    try:
        r.execute_command("CLUSTER", "INFO")
    except redis.ResponseError as exc:
        print(f"CLUSTER INFO: cluster support disabled on this single-node instance ({exc})")


if __name__ == "__main__":
    main()
