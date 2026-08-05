"""
Lesson 32: watching a graph run step by step, locally, no external service.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/03_advanced/32_tracing_and_observability/lesson.py

Lesson 8 introduced stream_mode="updates". This lesson uses
stream_mode="debug", which emits a "task" event when a node starts and a
"task_result" event when it finishes, each carrying a timestamp, letting
us reconstruct exactly which node ran, in what order, and how long it
took, entirely locally. No LangSmith, no extra API keys, nothing beyond
what every earlier lesson already required.
"""

from datetime import datetime

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

load_dotenv()


class State(TypedDict):
    count: int


def increment(state: State) -> dict:
    return {"count": state["count"] + 1}


def route_after_increment(state: State) -> str:
    # The loop: keep incrementing until count reaches 3.
    return "increment" if state["count"] < 3 else "classify"


def classify(state: State) -> dict:
    return {}


def route_after_classify(state: State) -> str:
    # The branch: even vs odd, decided after the loop finishes.
    return "even_path" if state["count"] % 2 == 0 else "odd_path"


def even_path(state: State) -> dict:
    return {}


def odd_path(state: State) -> dict:
    return {}


builder = StateGraph(State)
builder.add_node("increment", increment)
builder.add_node("classify", classify)
builder.add_node("even_path", even_path)
builder.add_node("odd_path", odd_path)
builder.add_edge(START, "increment")
builder.add_conditional_edges("increment", route_after_increment)
builder.add_conditional_edges("classify", route_after_classify)
builder.add_edge("even_path", END)
builder.add_edge("odd_path", END)
app = builder.compile()


def main() -> None:
    # A dict of task id -> start timestamp, so we can compute elapsed
    # time once that same task's "task_result" event arrives.
    started_at: dict[str, datetime] = {}

    for event in app.stream({"count": 0}, stream_mode="debug"):
        payload = event["payload"]
        task_id = payload["id"]

        if event["type"] == "task":
            started_at[task_id] = datetime.fromisoformat(event["timestamp"])
            print(f"[step {event['step']}] -> entering {payload['name']} (input={payload['input']})")

        elif event["type"] == "task_result":
            elapsed = datetime.fromisoformat(event["timestamp"]) - started_at[task_id]
            print(
                f"[step {event['step']}] <- leaving  {payload['name']} "
                f"(result={payload['result']}, took {elapsed.total_seconds() * 1000:.2f}ms)"
            )

    print("\nThat trace shows the loop running three times (increment), then the")
    print("branch picking exactly one of even_path/odd_path, all without a single")
    print("print statement written inside the nodes themselves.")


if __name__ == "__main__":
    main()
