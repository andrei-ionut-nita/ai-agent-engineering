"""
Lesson 2: what's in the compose file, and confirming the stack
image's modules loaded.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Redis is running first):

    docker compose up -d redis
    uv run python lessons/redis/01_beginner/02_running_redis_via_docker_compose/lesson.py
"""

import os

import redis
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    dsn = os.environ["REDIS_DSN"]
    r = redis.Redis.from_url(dsn, decode_responses=True)

    # MODULE LIST has no typed helper on the client, execute_command
    # sends any command verbatim, the raw-SQL equivalent for Redis. Each
    # module comes back as a flat [key, value, key, value, ...] list.
    modules = r.execute_command("MODULE", "LIST")
    module_names = sorted(dict(zip(m[::2], m[1::2]))["name"] for m in modules)

    print(f"Loaded modules: {', '.join(module_names)}")
    print(f"search module present: {'search' in module_names}")
    print(f"ReJSON module present: {'ReJSON' in module_names}")


if __name__ == "__main__":
    main()
