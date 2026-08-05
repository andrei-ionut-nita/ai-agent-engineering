"""
Lesson 22 (Checkpoint project): a persistent, human-in-the-loop content
publishing workflow.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/02_intermediate/22_intermediate_checkpoint_project/lesson.py

This combines four things from this tier into one graph: a SqliteSaver
checkpointer (Lesson 14) giving each draft's workflow real, on-disk
memory under its own thread_id (Lesson 13), an interrupt() that pauses
before publishing anything until a human approves it (Lesson 15), a
Command that both records the approval decision and routes to publish
or reject in one step (Lesson 20), and a RetryPolicy (Lesson 21) on the
"publish" step, standing in for a flaky real-world publishing API.
"""

from pathlib import Path
from typing import Literal

from typing_extensions import TypedDict

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, RetryPolicy, interrupt

load_dotenv()

DB_PATH = Path(__file__).parent / "publishing.sqlite"
model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


class PublishError(Exception):
    """Stands in for a transient failure from a real publishing API.

    Deliberately not a ValueError: LangGraph's default RetryPolicy does
    not retry ValueError (see Lesson 21), only exceptions that look like
    transient infrastructure failures.
    """


# A module-level counter, not randomness, so the "publish fails once
# then succeeds" behavior is reproducible every time this lesson runs,
# same technique as Lesson 21.
publish_attempts = 0


class PublishState(TypedDict):
    topic: str
    draft: str
    approved: bool
    published: bool


def write_draft(state: PublishState) -> dict:
    response = model.invoke(
        f"Write a two-sentence blog post announcement about: {state['topic']}"
    )
    return {"draft": response.text.strip()}


def request_approval(state: PublishState) -> Command[Literal["publish", "reject"]]:
    # Pauses here. The checkpointer (SqliteSaver, wired in below) is what
    # makes it safe for real time to pass between this pause and whenever
    # a human actually responds, exactly like Lesson 15, just now backed
    # by a real file instead of InMemorySaver.
    decision = interrupt(
        {
            "question": "Approve this draft for publishing?",
            "draft": state["draft"],
        }
    )
    # One node both records the decision AND routes, no separate
    # add_conditional_edges call needed for this, same pattern as
    # Lesson 20.
    if decision:
        return Command(update={"approved": True}, goto="publish")
    return Command(update={"approved": False}, goto="reject")


def publish(state: PublishState) -> dict:
    global publish_attempts
    publish_attempts += 1
    if publish_attempts == 1:
        # The first publish attempt across the whole demo fails, to show
        # the RetryPolicy below recovering from it automatically.
        raise PublishError("publishing service briefly unavailable")
    return {"published": True}


def reject(state: PublishState) -> dict:
    return {"published": False}


builder = StateGraph(PublishState)
builder.add_node("write_draft", write_draft)
builder.add_node("request_approval", request_approval)
# retry_policy here means a transient publish failure gets retried
# automatically instead of failing the whole workflow, same as Lesson 21.
builder.add_node("publish", publish, retry_policy=RetryPolicy(max_attempts=3, initial_interval=0.1))
builder.add_node("reject", reject)

builder.add_edge(START, "write_draft")
builder.add_edge("write_draft", "request_approval")
# No add_conditional_edges for request_approval: its Command return
# value already says where to go.
builder.add_edge("publish", END)
builder.add_edge("reject", END)


def run_workflow(topic: str, thread_id: str, approve: bool, checkpointer) -> None:
    app = builder.compile(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": thread_id}}

    result = app.invoke(
        {"topic": topic, "draft": "", "approved": False, "published": False}, config
    )

    pending = result["__interrupt__"]
    print(f"Topic: {topic}")
    print(f"  Draft: {pending[0].value['draft']}")
    print(f"  Paused, awaiting approval...")

    # In a real app this resume would be a separate request, made later,
    # by an actual reviewer (Lesson 15). Here we simulate it immediately.
    final = app.invoke(Command(resume=approve), config)
    if final["published"]:
        print("  -> Published!")
    else:
        print("  -> Rejected, never published.")
    print()


def main() -> None:
    # Fresh database each run, so the lesson's output is predictable to
    # read here. In a real app you would NOT do this, the whole point of
    # SqliteSaver (Lesson 14) is that the file persists across restarts.
    if DB_PATH.exists():
        DB_PATH.unlink()

    with SqliteSaver.from_conn_string(str(DB_PATH)) as checkpointer:
        # First workflow: approved. Its publish step deliberately fails
        # once (publish_attempts == 1) and the RetryPolicy recovers.
        run_workflow(
            "our new open-source CLI tool",
            thread_id="post-1",
            approve=True,
            checkpointer=checkpointer,
        )

        # Second workflow: rejected, a completely separate thread_id, so
        # it shares nothing with post-1 except the same compiled graph
        # and the same underlying .sqlite file.
        run_workflow(
            "a controversial pricing change",
            thread_id="post-2",
            approve=False,
            checkpointer=checkpointer,
        )

    print(f"All workflow state persisted in: {DB_PATH}")


if __name__ == "__main__":
    main()
