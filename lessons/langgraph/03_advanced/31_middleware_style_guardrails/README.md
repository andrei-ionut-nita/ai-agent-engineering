# Lesson 31: Middleware-style guardrails, as plain nodes

## What middleware actually is

The langchain course's `@before_model` (langchain course, lesson 33)
looked like a special mechanism: a decorator that hooks into an agent's
loop and runs automatically. Underneath, it's simpler than the decorator
makes it look, it's just an extra node, wired in before the "real" work.
This lesson builds that same effect with nothing but nodes and edges,
no decorator, no hidden wrapping, so the mechanism is fully visible.

## A guardrail is a node like any other

```python
def input_guardrail(state: State) -> dict:
    text = state["question"].lower()
    if any(word in text for word in BANNED_WORDS):
        return {"blocked_reason": "request mentions restricted information"}
    if len(state["question"]) > MAX_INPUT_LENGTH:
        return {"blocked_reason": "request is too long"}
    return {"blocked_reason": ""}
```

Nothing about this function's shape is different from any node you've
written since Beginner Lesson 3. It reads state, returns a dict. Its
"guardrail" behavior comes entirely from what it checks and where it's
placed in the graph, not from any special API.

## Placement is the whole mechanism

```python
builder.add_edge(START, "input_guardrail")
builder.add_conditional_edges("input_guardrail", route_after_input_guard)
builder.add_edge("generate", "output_guardrail")
builder.add_edge("output_guardrail", END)
```

`input_guardrail` runs first, before `generate` (the actual model call)
is ever reached. Its conditional edge either continues to `generate` or
routes straight to `END`, meaning the model is **never called** if a
guardrail trips. `output_guardrail` runs after `generate`, checking what
came back before it's considered final. `@before_model` and
`@after_model` are just names for this exact pattern: a node positioned
before, and a node positioned after.

## Two independent checks, one input guardrail

```python
BANNED_WORDS = {"confidential", "password"}
MAX_INPUT_LENGTH = 300
```

Two unrelated rules checked in the same node: a banned-word filter and a
length cap. Nothing requires guardrails to live in separate nodes,
grouping related checks together is a normal design choice, the same way
you'd group related validation logic in any function.

## Running it

```bash
uv run python lessons/langgraph/03_advanced/31_middleware_style_guardrails/lesson.py
```

The first question passes through untouched. The second mentions
"confidential" and gets blocked before `generate` ever runs, the printed
output makes clear the model was never called for that turn at all.

## Checkpoint

- **middleware is a node**: `@before_model`/`@after_model` decorators
  wrap exactly this pattern, an extra node positioned before or after
  the real work.
- **blocking before the model runs**: a conditional edge that routes
  around `generate` entirely prevents the model from ever seeing a
  disallowed request.
- **output guardrails**: a node placed after generation can inspect or
  modify what came back before it's treated as final.
- **why it's just wiring**: no special decorator or framework feature is
  required, `add_node` and `add_conditional_edges` are enough.

If anything here still feels unclear, ask before moving to Lesson 32.
