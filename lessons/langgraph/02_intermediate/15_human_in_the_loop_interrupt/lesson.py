"""
Lesson 15: interrupt(), pausing a graph mid-run for a human.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/02_intermediate/15_human_in_the_loop_interrupt/lesson.py

Every graph so far has run start to finish with no stopping point. This
lesson adds a node that calls interrupt(), which pauses the graph and
hands a payload back to whoever called .invoke(), before that node's
work is considered done. In this script we simulate the human by calling
.invoke(Command(resume=...)) immediately afterward with a hardcoded
answer, but in a real app that second call would come from a separate
request, made by an actual person, possibly minutes or days later.
"""

from typing_extensions import TypedDict

from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

load_dotenv()


class ExpenseState(TypedDict):
    amount: int
    reason: str
    approved: bool
    result: str


def request_approval(state: ExpenseState) -> dict:
    # interrupt(value) pauses the graph right here. `value` is whatever
    # a human reviewer needs to see to make a decision. The first time
    # this line runs, it doesn't return, it raises internally and the
    # graph halts, its state already saved by the checkpointer.
    decision = interrupt(
        {
            "question": f"Approve expense of ${state['amount']} for '{state['reason']}'?",
        }
    )
    # This line only runs AFTER a resume happens, and it runs on a
    # re-execution of this same node from the top, with `decision` now
    # holding whatever was passed to Command(resume=...).
    return {"approved": decision}


def process_expense(state: ExpenseState) -> dict:
    if state["approved"]:
        return {"result": f"Expense of ${state['amount']} approved and processed."}
    return {"result": f"Expense of ${state['amount']} was rejected."}


builder = StateGraph(ExpenseState)
builder.add_node("request_approval", request_approval)
builder.add_node("process_expense", process_expense)
builder.add_edge(START, "request_approval")
builder.add_edge("request_approval", "process_expense")
builder.add_edge("process_expense", END)

# interrupt() requires a checkpointer: pausing only makes sense if the
# in-progress state is actually saved somewhere in the meantime.
app = builder.compile(checkpointer=InMemorySaver())


def main() -> None:
    config = {"configurable": {"thread_id": "expense-1"}}

    # First call: runs request_approval, hits interrupt(), and returns
    # WITHOUT ever reaching process_expense. Verified against the real
    # 1.2.10 API: the result dict itself carries an "__interrupt__" key
    # rather than raising, holding a list of Interrupt objects.
    result = app.invoke(
        {"amount": 500, "reason": "team lunch", "approved": False, "result": ""},
        config,
    )

    pending = result["__interrupt__"]
    print("Graph paused. Pending question:")
    print(" ", pending[0].value["question"])

    # In a real app, this is the line that would NOT run right away.
    # Instead, the payload above would be shown to a human in some UI,
    # and this Command(resume=...) call would happen later, from a
    # separate process or request, once they actually answered. Here we
    # simulate an approval immediately, purely for demo purposes.
    print("\n(Simulating a human approving this, right now, for the demo.)")
    final = app.invoke(Command(resume=True), config)
    print("Final state:", final["result"])

    # A second thread, this time simulating a rejection.
    config2 = {"configurable": {"thread_id": "expense-2"}}
    result2 = app.invoke(
        {"amount": 5000, "reason": "gold-plated stapler", "approved": False, "result": ""},
        config2,
    )
    print("\nGraph paused. Pending question:")
    print(" ", result2["__interrupt__"][0].value["question"])
    print("(Simulating a human rejecting this, right now, for the demo.)")
    final2 = app.invoke(Command(resume=False), config2)
    print("Final state:", final2["result"])


if __name__ == "__main__":
    main()
