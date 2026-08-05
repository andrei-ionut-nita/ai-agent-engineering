# Lesson 20: Human-in-the-loop with deferred tools

## Not every tool should just run

Lesson 6-7's tools executed immediately whenever the model called them.
For anything destructive or costly, deleting a file, sending an email,
issuing a refund, you often want a human to approve the call *before*
it runs. `requires_approval=True` on a tool turns "call it" into
"pause and ask."

```python
@agent.tool_plain(requires_approval=True)
def delete_file(path: str) -> str:
    """Delete a file at the given path."""
    return f"deleted {path}"
```

## What happens when an approval-gated tool is called

Instead of running the tool, the agent's run ends early and
`result.output` comes back as a `DeferredToolRequests`, holding the
pending calls that need a decision, not your normal `output_type`.
Declare that this can happen by including it in `output_type`:

```python
from pydantic_ai.tools import DeferredToolRequests

agent = Agent("google:gemini-3.5-flash-lite", output_type=[str, DeferredToolRequests])
```

## Resuming after a decision

Once a human (or your own policy code) approves or rejects each
pending call, build a `DeferredToolResults` and run again, passing the
prior message history back in:

```python
from pydantic_ai.tools import DeferredToolResults

results = DeferredToolResults()
for call in output.approvals:
    results.approvals[call.tool_call_id] = True  # or False to reject

final = agent.run_sync(
    message_history=result.all_messages(),
    deferred_tool_results=results,
)
```

The agent picks up exactly where it left off: approved tools actually
run, rejected ones don't, and the run continues toward a real final
answer. This is the Pydantic AI equivalent of LangGraph's
interrupt-and-resume pattern for human approval, just modeled as a
distinct output type instead of a graph interrupt.

## Running it

```bash
uv run python lessons/pydantic_ai/03_advanced/20_human_in_the_loop_deferred_tools/lesson.py
```

This lesson uses `TestModel` (Lesson 14) rather than a live Gemini
call, so the approval flow is deterministic and needs no API key: the
point here is the approve/resume mechanics, not what a real model
decides to call.

## Checkpoint

- `requires_approval=True` on a tool turns a call into a pending
  request instead of an immediate execution.
- `output_type` must include `DeferredToolRequests` for this to be a
  valid outcome of a run.
- `DeferredToolResults` plus the prior `message_history` resumes the
  run, executing approved calls and skipping rejected ones.

If anything here still feels unclear, ask before moving to Lesson 21.
