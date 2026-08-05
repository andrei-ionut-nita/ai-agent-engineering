"""
Lesson 21: RetryPolicy, a node that recovers from failure automatically.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/02_intermediate/21_retry_and_error_handling/lesson.py

Every node so far has assumed it just works. Real nodes call flaky
things: APIs that time out, services that are briefly overloaded. This
lesson wraps a deliberately flaky function in a node with a RetryPolicy,
so LangGraph retries it automatically on failure, then shows what
happens to the exact same kind of failure with no retry policy at all,
for contrast.
"""

from typing_extensions import TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy

load_dotenv()


class FlakyServiceError(Exception):
    """Stands in for a real transient failure, like a timed-out API call.

    LangGraph's default retry_on policy deliberately does NOT retry
    ValueError, TypeError, and several other common "this input was
    just wrong" exceptions, only things that look like transient
    infrastructure failures (connection errors, 5xx responses, or, as
    here, an exception type outside its "assume this won't fix itself"
    list). A plain ValueError would silently NOT be retried, verified
    directly against this project's installed LangGraph.
    """


# A module-level counter makes this demo deterministic: the third call
# always succeeds, no randomness, so the lesson's output is reproducible
# every time you run it.
attempt_count = 0


def unreliable_call(state: dict) -> dict:
    global attempt_count
    attempt_count += 1
    print(f"  attempt {attempt_count}...")
    if attempt_count < 3:
        raise FlakyServiceError(f"simulated failure on attempt {attempt_count}")
    return {"result": "success"}


class RetryState(TypedDict):
    result: str


retry_builder = StateGraph(RetryState)
# retry_policy is a normal add_node keyword argument, not something that
# needs a separate wiring step. max_attempts=3 means: try once, and on
# failure retry up to 2 more times (3 attempts total) before giving up
# and letting the exception propagate for real.
retry_builder.add_node(
    "unreliable_call",
    unreliable_call,
    retry_policy=RetryPolicy(max_attempts=3, initial_interval=0.1),
)
retry_builder.add_edge(START, "unreliable_call")
retry_builder.add_edge("unreliable_call", END)
app_with_retry = retry_builder.compile()


def main() -> None:
    global attempt_count

    print("With a RetryPolicy attached (max_attempts=3):")
    attempt_count = 0
    result = app_with_retry.invoke({"result": ""})
    print(f"  Final result: {result['result']}\n")

    # Now the same kind of flaky failure, but on a node with NO retry
    # policy at all, to show what happens without one.
    print("With no RetryPolicy at all:")
    attempt_count = 0

    no_retry_builder = StateGraph(RetryState)
    no_retry_builder.add_node("unreliable_call", unreliable_call)  # no retry_policy=
    no_retry_builder.add_edge(START, "unreliable_call")
    no_retry_builder.add_edge("unreliable_call", END)
    app_without_retry = no_retry_builder.compile()

    try:
        app_without_retry.invoke({"result": ""})
    except FlakyServiceError as exc:
        # Without a retry policy, the very first failure propagates
        # straight out of .invoke() as a real exception, no second
        # attempt ever happens. We catch it here only so the demo script
        # can finish and print its point clearly, a real caller would
        # need to decide how to handle this itself.
        print(f"  Uncaught after the FIRST attempt: {exc!r}")
        print("  (No retries happened, unlike the version above.)")


if __name__ == "__main__":
    main()
