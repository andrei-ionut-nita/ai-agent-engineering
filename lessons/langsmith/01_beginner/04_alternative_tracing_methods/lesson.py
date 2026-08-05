"""
Lesson 4: tracing without the @traceable decorator.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langsmith/01_beginner/04_alternative_tracing_methods/lesson.py
"""

from dotenv import load_dotenv
from langsmith import trace
from langsmith.run_trees import RunTree

load_dotenv()


def legacy_multiply(a: int, b: int) -> int:
    # An ordinary function we don't want to (or can't) put @traceable on
    # directly, imagine this came from a library we don't control.
    return a * b


def trace_with_context_manager() -> None:
    # trace() does the same job as @traceable, but wraps a block of code
    # instead of a whole function. Useful when you only want to trace
    # part of a function, or when the code isn't a function you can
    # decorate at all.
    with trace(name="legacy_multiply", run_type="tool", inputs={"a": 6, "b": 7}) as run:
        result = legacy_multiply(6, 7)
        run.end(outputs={"result": result})
    print(f"context manager result: {result}")


def trace_with_run_tree() -> None:
    # RunTree is the lowest-level way to create a run: build it by hand,
    # post it yourself. @traceable and trace() are both convenience
    # layers built on top of this same object.
    run = RunTree(
        name="manual_run_tree",
        run_type="chain",
        inputs={"message": "built by hand"},
    )
    run.post()
    output = "processed: built by hand"
    run.end(outputs={"output": output})
    run.patch()
    print(f"RunTree result: {output}")


def main() -> None:
    trace_with_context_manager()
    trace_with_run_tree()


if __name__ == "__main__":
    main()
