"""
Lesson 30: dynamic breakpoints, pausing only when a runtime condition says so.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/03_advanced/30_dynamic_breakpoints/lesson.py

Lesson 15's interrupt() always paused, unconditionally, wherever it was
called. This lesson contrasts two ways to pause: a STATIC breakpoint via
compile(interrupt_before=[...]) (pauses before a node, every single
time, no exceptions), and a DYNAMIC breakpoint, a node that only calls
interrupt() when some runtime condition is met, here, a dollar amount
over a threshold.
"""

from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from typing_extensions import TypedDict

load_dotenv()

APPROVAL_THRESHOLD = 500


class State(TypedDict):
    amount: float
    approved: bool
    result: str


def process_payment(state: State) -> dict:
    return {"result": f"Payment of ${state['amount']:.2f} processed."}


def maybe_require_approval(state: State) -> dict:
    # This is the DYNAMIC part: the node runs every time, but it only
    # calls interrupt() when the amount crosses the threshold. Small
    # payments sail through with no pause at all, same compiled graph,
    # different behavior depending on the data.
    if state["amount"] > APPROVAL_THRESHOLD:
        decision = interrupt(
            f"Payment of ${state['amount']:.2f} exceeds ${APPROVAL_THRESHOLD}. Approve? (yes/no)"
        )
        return {"approved": str(decision).strip().lower() in {"yes", "y"}}
    return {"approved": True}


def route_after_approval(state: State) -> str:
    return "process_payment" if state["approved"] else END


builder = StateGraph(State)
builder.add_node("maybe_require_approval", maybe_require_approval)
builder.add_node("process_payment", process_payment)
builder.add_edge(START, "maybe_require_approval")
builder.add_conditional_edges("maybe_require_approval", route_after_approval)
builder.add_edge("process_payment", END)
# interrupt() needs a checkpointer to persist state across the pause,
# same requirement as Lesson 15.
dynamic_app = builder.compile(checkpointer=InMemorySaver())


def run_dynamic(amount: float, approve_with: str | None) -> None:
    config = {"configurable": {"thread_id": f"payment-{amount}"}}
    result = dynamic_app.invoke({"amount": amount, "approved": False, "result": ""}, config)

    if "__interrupt__" in result:
        # The graph paused mid-run. Resuming with Command(resume=...)
        # feeds the value straight back as interrupt()'s return value,
        # and the node re-runs from its start with that answer in hand.
        print(f"  [paused] {result['__interrupt__'][0].value}")
        result = dynamic_app.invoke(Command(resume=approve_with), config)

    print(f"  final: {result['result'] or '(not processed, rejected)'}\n")


# --- Static breakpoint, for contrast: pauses before EVERY run, no matter
# the amount, because it's declared at compile time, not decided by the
# node's own logic. ---
static_builder = StateGraph(State)
static_builder.add_node("process_payment", process_payment)
static_builder.add_edge(START, "process_payment")
static_builder.add_edge("process_payment", END)
static_app = static_builder.compile(
    checkpointer=InMemorySaver(),
    interrupt_before=["process_payment"],
)


def run_static(amount: float) -> None:
    config = {"configurable": {"thread_id": f"static-{amount}"}}
    result = static_app.invoke({"amount": amount, "approved": True, "result": ""}, config)
    print(f"  [paused before process_payment, unconditionally, amount=${amount:.2f}]")
    # Resuming with Command(resume=...) isn't even needed here, there's
    # no interrupt() call waiting for a value, just invoke again to let
    # the graph continue past the static breakpoint.
    result = static_app.invoke(None, config)
    print(f"  final: {result['result']}\n")


def main() -> None:
    print("Dynamic breakpoint: only pauses over the threshold.")
    print(f"Small payment (${300}):")
    run_dynamic(300, approve_with=None)
    print(f"Large payment (${900}), approved:")
    run_dynamic(900, approve_with="yes")
    print(f"Large payment (${900}), rejected:")
    run_dynamic(900, approve_with="no")

    print("Static breakpoint: pauses every time, regardless of amount.")
    run_static(50)


if __name__ == "__main__":
    main()
