"""
Lesson 16: get_state_history(), rewinding and forking a run.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/02_intermediate/16_time_travel_state_history/lesson.py

Lessons 13-15 all relied on a checkpointer saving state so memory could
survive between calls. This lesson looks directly at what a checkpointer
actually stores: a snapshot after every single node, not just the final
result. get_state_history() lists all of them, and passing an old
snapshot's checkpoint_id back into a call rewinds the graph to that
exact point and re-runs forward from there.
"""

import operator
from typing import Annotated

from typing_extensions import TypedDict

from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

load_dotenv()


class PipelineState(TypedDict):
    # operator.add so each node's single-item list gets appended to the
    # running log instead of overwriting it, same idea as Lesson 2.
    steps: Annotated[list[str], operator.add]
    total: int


def step1(state: PipelineState) -> dict:
    return {"steps": ["step1"], "total": state["total"] + 1}


def step2(state: PipelineState) -> dict:
    return {"steps": ["step2"], "total": state["total"] + 10}


def step3(state: PipelineState) -> dict:
    return {"steps": ["step3"], "total": state["total"] + 100}


builder = StateGraph(PipelineState)
builder.add_node("step1", step1)
builder.add_node("step2", step2)
builder.add_node("step3", step3)
builder.add_edge(START, "step1")
builder.add_edge("step1", "step2")
builder.add_edge("step2", "step3")
builder.add_edge("step3", END)

app = builder.compile(checkpointer=InMemorySaver())


def main() -> None:
    config = {"configurable": {"thread_id": "history-demo"}}

    result = app.invoke({"steps": [], "total": 0}, config)
    print("Final state after a normal run:", result)

    # get_state_history() yields one StateSnapshot per checkpoint, newest
    # first: one after START, one after each node finishes. `.next` tells
    # you which node was about to run when that snapshot was taken, empty
    # once the graph has reached END.
    history = list(app.get_state_history(config))
    print(f"\n{len(history)} snapshots saved for this thread:")
    for snap in history:
        checkpoint_id = snap.config["configurable"]["checkpoint_id"]
        print(f"  next={snap.next!r:16} values={snap.values} id={checkpoint_id[:8]}...")

    # Find the snapshot taken right after step1 finished, i.e. the point
    # where step2 was about to run next.
    before_step2 = next(snap for snap in history if snap.next == ("step2",))
    print("\nRewinding to right before step2 ran:", before_step2.values)

    # Passing that snapshot's checkpoint_id back in, alongside the same
    # thread_id, tells the graph to resume from THAT point in history,
    # not from wherever the thread currently sits. Passing None as the
    # input (like resuming after Lesson 15's interrupt) means "just
    # continue forward from here."
    fork_config = {
        "configurable": {
            "thread_id": "history-demo",
            "checkpoint_id": before_step2.config["configurable"]["checkpoint_id"],
        }
    }
    replayed = app.invoke(None, fork_config)
    print("Result after re-running step2 and step3 from that rewind point:")
    print(" ", replayed)


if __name__ == "__main__":
    main()
