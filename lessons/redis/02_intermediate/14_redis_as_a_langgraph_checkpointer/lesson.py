"""
Lesson 14: RedisSaver, a LangGraph checkpointer backed by Redis.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Redis is running first):

    docker compose up -d redis
    uv run python lessons/redis/02_intermediate/14_redis_as_a_langgraph_checkpointer/lesson.py
"""

import os

from dotenv import load_dotenv
from langgraph.checkpoint.redis import RedisSaver
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

load_dotenv()


class State(TypedDict):
    count: int


def increment(state: State) -> State:
    return {"count": state["count"] + 1}


def main() -> None:
    dsn = os.environ["REDIS_DSN"]

    with RedisSaver.from_conn_string(dsn) as checkpointer:
        checkpointer.setup()

        graph = StateGraph(State)
        graph.add_node("increment", increment)
        graph.add_edge(START, "increment")
        graph.add_edge("increment", END)
        app = graph.compile(checkpointer=checkpointer)

        config = {"configurable": {"thread_id": "user-42"}}

        first = app.invoke({"count": 0}, config)
        print(f"First invoke (fresh state):  {first}")

        # Same thread_id: LangGraph loads the checkpoint RedisSaver
        # wrote for the first call and continues from there.
        second = app.invoke({"count": 5}, config)
        print(f"Second invoke (same thread): {second}")

        state = app.get_state(config)
        print(f"State after both calls:      {state.values}")


if __name__ == "__main__":
    main()
