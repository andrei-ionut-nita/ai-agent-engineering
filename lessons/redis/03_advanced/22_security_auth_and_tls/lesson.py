"""
Lesson 22: ACL SETUSER, a scoped Redis user for one agent.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Redis is running first):

    docker compose up -d redis
    uv run python lessons/redis/03_advanced/22_security_auth_and_tls/lesson.py
"""

import os

import redis
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    dsn = os.environ["REDIS_DSN"]
    r = redis.Redis.from_url(dsn, decode_responses=True)

    print(f"Default user: {r.execute_command('ACL', 'WHOAMI')}")

    r.execute_command("ACL", "DELUSER", "agent")
    r.execute_command(
        "ACL",
        "SETUSER",
        "agent",
        "on",
        ">agentpass",
        "~session:*",
        "+get",
        "+set",
        "+setex",
        "+ping",
    )
    print("Created scoped user 'agent'")

    agent_conn = redis.Redis.from_url(
        "redis://agent:agentpass@localhost:6379", decode_responses=True
    )
    print(f"agent PING -> {agent_conn.ping()}")

    agent_conn.set("session:1", "active")
    print("agent SET session:1 -> allowed")

    try:
        agent_conn.set("other:key", "x")
    except redis.ResponseError as exc:
        print(f"agent SET other:key -> denied: {exc}")

    try:
        agent_conn.flushall()
    except redis.ResponseError as exc:
        print(f"agent FLUSHALL -> denied: {exc}")

    r.execute_command("ACL", "DELUSER", "agent")


if __name__ == "__main__":
    main()
