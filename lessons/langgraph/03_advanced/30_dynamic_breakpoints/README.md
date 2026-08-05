# Lesson 30: Dynamic breakpoints

## Two ways to pause, and when each one fits

Intermediate Lesson 15's `interrupt()` always paused, unconditionally,
wherever it was called. That's the right fit when every single run needs
a human to look at it. But often, only *some* runs deserve a pause, a
$5 purchase doesn't need approval, a $50,000 one does. This lesson
covers both mechanisms side by side: a **static** breakpoint, declared
once at compile time, that pauses every run without exception, and a
**dynamic** breakpoint, a node that only calls `interrupt()` when a
runtime condition is actually met.

## The dynamic breakpoint: a node that sometimes pauses

```python
def maybe_require_approval(state: State) -> dict:
    if state["amount"] > APPROVAL_THRESHOLD:
        decision = interrupt(
            f"Payment of ${state['amount']:.2f} exceeds ${APPROVAL_THRESHOLD}. Approve? (yes/no)"
        )
        return {"approved": str(decision).strip().lower() in {"yes", "y"}}
    return {"approved": True}
```

This node runs on *every* invocation, but `interrupt()` is only reached
when the condition is true. A $300 payment sails straight through with
no pause at all, an $900 payment stops here and waits. Same compiled
graph, same node, different behavior, entirely driven by the data.

## The static breakpoint: pauses no matter what

```python
static_app = static_builder.compile(
    checkpointer=InMemorySaver(),
    interrupt_before=["process_payment"],
)
```

`interrupt_before=["process_payment"]` is a compile-time declaration:
before this node ever runs, for any input, pause. There's no
`interrupt()` call inside `process_payment` at all, and no condition to
check, the pause is unconditional and lives entirely outside the node's
own code.

## Resuming each kind

```python
# Dynamic: interrupt() is waiting for a specific value.
result = dynamic_app.invoke(Command(resume=approve_with), config)

# Static: nothing is waiting for a value, just continue past the pause.
result = static_app.invoke(None, config)
```

Both use the same underlying checkpointer-backed pause/resume mechanism
from Lesson 15. The difference is only in what resuming means: a dynamic
breakpoint's `interrupt()` call is waiting for a specific answer
(`Command(resume=...)` supplies it), while a static breakpoint has no
`interrupt()` call to satisfy, invoking with `None` simply lets the
graph proceed past wherever it paused.

## Running it

```bash
uv run python lessons/langgraph/03_advanced/30_dynamic_breakpoints/lesson.py
```

Watch the $300 payment process without any pause, the $900 payment pause
and wait for approval (shown both approved and rejected), and the static
breakpoint pause for a mere $50, purely because it was declared to
always pause, with no condition involved.

## Checkpoint

- **static breakpoint**: `compile(interrupt_before=[...])`, pauses
  before a named node, every single run, unconditionally.
- **dynamic breakpoint**: a node that calls `interrupt()` only when a
  runtime condition is met, same node runs every time, the pause doesn't.
- **`Command(resume=...)`**: supplies the value an `interrupt()` call is
  waiting for.
- **resuming a static breakpoint**: `invoke(None, config)`, there's no
  value to supply, just permission to continue.

If anything here still feels unclear, ask before moving to Lesson 31.
