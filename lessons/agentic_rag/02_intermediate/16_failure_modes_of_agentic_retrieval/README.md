# Lesson 16: Failure Modes of Agentic Retrieval

## Where we left off

This is this course's centerpiece lesson. Every earlier Intermediate
lesson assumed things go right: the model asks for a sensible call, the
tool returns a clean result, the loop converges in a step or two. Real
function-calling systems don't get that luxury reliably, and this
lesson studies three specific, distinct ways they fail, each one
actually triggered in code below, not just described in prose.

## Three failure modes, kept distinct on purpose

It's tempting to lump "the agent messed up" into one category. These
three are genuinely different problems with genuinely different fixes,
conflating them leads to fixing the wrong thing:

1. **A malformed or erroring tool call.** The model requests a real
   tool, but with missing or invalid arguments, or the tool itself
   raises. This is a *code-level* failure: something crashes unless you
   catch it.
2. **Unnecessary retrieval.** The model calls a tool it didn't need,
   for a question it could have answered directly. This is a
   *judgment-level* failure: nothing crashes, the answer might even be
   fine, but cost and latency were spent for nothing, the same waste
   Lesson 2 demonstrated the fixed pipeline paying unconditionally,
   now showing up occasionally even in an agentic loop that's supposed
   to avoid it.
3. **A non-converging loop.** The model keeps requesting calls and
   never settles on a final answer. This is a *termination* failure:
   without a bound, the loop simply doesn't stop.

## The code, piece by piece

### Failure mode 1: malformed calls, deliberately triggered

```python
def malformed_call_stub() -> GenerateFn:
    ...
    malformed = types.FunctionCall(name="search_notes", args={})
```

Rather than hope the live model happens to send a malformed call during
this run (unreliable, and impossible to verify offline while today's
`GOOGLE_API_KEY` is quota-exhausted), this lesson constructs one
directly: a `FunctionCall` for `search_notes` with an empty `args`
dict, missing the required `query` argument entirely. `ask()` accepts a
swappable `generate_fn`, so this fake response stands in for a real API
call, and the rest of the loop runs unmodified.

```python
def run_tool_safe(call: types.FunctionCall, store: list[dict]) -> dict[str, str]:
    try:
        args = call.args or {}
        if call.name == "search_notes":
            return {"output": search_notes(args["query"], store)}
        ...
    except Exception as error:
        return {"error": f"{type(error).__name__}: {error}"}
```

`args["query"]` raises `KeyError` on the malformed call above.
`run_tool_safe()` catches *any* exception, not just this one
(`get_current_datetime()`'s uncaught `ZoneInfoNotFoundError` on a bad
timezone name goes through the same path), and turns it into a
`{"error": ...}` dict. `FunctionResponse.response` explicitly supports
an `"error"` key for exactly this (see the SDK's own docstring on
`FunctionResponse`), the model sees that the call failed and why,
instead of the whole loop crashing.

### Failure mode 2: unnecessary retrieval, observed live

```python
ambiguous_question = "What's a good daily routine for building a new skill?"
answer, steps, hit_limit = ask(ambiguous_question, store)
```

Unlike failure mode 1, this one runs against the real model (no stub),
because it's about the model's actual judgment, not something you'd
want to fake. The question is deliberately answerable generically, but
topically adjacent to `language-journal.md` ("routine", "skill"). A
nonzero step count here is the failure caught in the act: retrieval ran
even though it wasn't needed. This is inherently non-deterministic,
unlike failure mode 1, reported honestly in the code's own output
rather than asserted as guaranteed.

### Failure mode 3: non-convergence, deliberately triggered

```python
def non_converging_stub() -> GenerateFn:
    def stub(contents):
        call = types.FunctionCall(name="get_current_datetime", args={"timezone": "UTC"})
        ...
        return FakeResponse(function_calls=[call], ...)
    return stub
```

A stub that *always* returns a valid tool call, no matter what's
already in `contents`, simulating a model that never decides it has
enough information. Lesson 14's `MAX_STEPS` guard is what turns this
from "runs forever" into "stops at 4 steps with an honest message,"
exactly what that lesson built it for.

## Running it

```bash
uv run python lessons/agentic_rag/02_intermediate/16_failure_modes_of_agentic_retrieval/lesson.py
```

## Expected output

```
=== Failure mode 1: a malformed tool call ===
  steps: 1, hit_limit: False
  A: I couldn't search the notes, the request was missing required information.

=== Failure mode 2: unnecessary retrieval ===
  Q: What's a good daily routine for building a new skill?
  steps: 0 or 1 (varies by run), hit_limit: False
  A: <a generic answer, possibly grounded in language-journal.md if retrieval fired>

=== Failure mode 3: a non-converging loop ===
  steps: 4, hit_limit: True
  A: I wasn't able to fully answer this within the allowed number of search steps.
```

## Checkpoint

- **Malformed/erroring calls**: a code-level failure, fixed by
  wrapping every tool invocation (`run_tool_safe()`) so an exception
  becomes an `{"error": ...}` function response, not a crash.
- **Unnecessary retrieval**: a judgment-level failure, no crash, real
  cost, mitigated (never fully eliminated) by sharper tool descriptions
  and system instructions, the same lever Lessons 4, 6, and 11 already
  used.
- **Non-convergence**: a termination-level failure, fixed by
  Lesson 14's `MAX_STEPS` guard, demonstrated here with a stub that
  deliberately never stops asking.
- These three failures need three different fixes; treating them as
  one problem ("the agent is unreliable") tends to produce a fix for
  only one of them while leaving the other two live.
- **Try this yourself**: write a fourth stub, `bad_argument_stub()`,
  where `search_notes` is called with `{"query": 12345}` (a number, not
  a string) instead of a missing key entirely. Does `run_tool_safe()`
  handle it the same way? Should it?

If anything here still feels unclear, ask before moving to Lesson 17.
