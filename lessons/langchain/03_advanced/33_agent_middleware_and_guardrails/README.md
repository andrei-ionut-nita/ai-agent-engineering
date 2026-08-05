# Lesson 33: Middleware and guardrails

## How this differs from Lesson 30

Lesson 30's `interrupt_before` paused the agent so a **human** could
review and approve a specific tool call. That's the right tool for
genuinely ambiguous, high-stakes decisions. But some rules don't need a
human in the loop at all, they can be checked automatically, every
single time, by code. That's what **middleware** is for: running your
own logic automatically at specific points in the agent's loop, no human
required for the common case.

## Writing a guardrail with `@before_model`

```python
@before_model(can_jump_to=["end"])
def block_confidential_requests(state, runtime):
    last_message = state["messages"][-1]

    if "confidential" in last_message.text.lower():
        return {
            "jump_to": "end",
            "messages": [AIMessage("I can't help with requests involving confidential information.")],
        }

    return None
```

`@before_model` wraps a plain function so it runs automatically right
before every call to the model, with access to `state`, the agent's
current data, including `state["messages"]`, the full conversation so
far, same shape you've been reading since Lesson 23.

Two possible outcomes, and this function demonstrates both:

- **Return `None`**: no objection, this turn proceeds normally, straight
  to the model, exactly as if no middleware existed.
- **Return `{"jump_to": "end", "messages": [...]}`**: skip the model
  entirely for this turn. `"jump_to": "end"` tells the agent's loop to
  stop here, and the `AIMessage` we provide becomes the final answer
  instead of anything the model would have said.

`can_jump_to=["end"]` on the decorator is a declaration: this middleware
is allowed to end the turn early. Without listing `"end"` there, trying
to jump there would be an error, this is a safety mechanism so
middleware can't redirect the agent's flow to places it was never
authorized to.

## Attaching it to the agent

```python
agent = create_agent(model=model, middleware=[block_confidential_requests])
```

Same `create_agent` from every Advanced lesson so far, with one new
parameter. `middleware=[...]` is a list, you could attach several
different guardrails at once, each one gets a chance to run before every
model call.

## Two questions, two outcomes

```python
ask("What is 2 + 2?")
ask("Tell me the confidential details of the merger.")
```

The first question contains no banned word, `block_confidential_requests`
returns `None`, and the model answers normally: "2 + 2 = 4". The second
question contains "confidential", the model is **never even called**
for that turn, our canned refusal becomes the answer directly. This
matters: the guardrail isn't asking the model to refuse politely, it's
preventing the model from ever seeing the request in the first place.

## Why this matters beyond one keyword check

This lesson's check ("does this message contain the word
'confidential'") is deliberately simple, so the mechanism is easy to
see clearly. Real guardrails follow the exact same pattern for more
sophisticated checks: LangChain even ships a built-in
`PIIMiddleware` for detecting personal information, and a
`HumanInTheLoopMiddleware` that generalizes Lesson 30's approval
pattern into reusable middleware, rather than something you wire up by
hand each time.

The core idea stays the same regardless of complexity: intercept the
agent's loop automatically, at a well-defined point, before the part of
the system that's harder to fully control (the model itself) ever gets
involved.

## Running it

```bash
uv run python lessons/langchain/03_advanced/33_agent_middleware_and_guardrails/lesson.py
```

## Checkpoint

- **middleware**: code that runs automatically at specific points in an
  agent's loop, without needing a human to intervene each time.
- **`@before_model`**: runs right before every model call, can inspect
  or modify the current state.
- **`{"jump_to": "end", ...}`**: skips the model entirely for this turn,
  substituting your own message as the final answer.
- **why it matters**: enforces rules automatically and consistently,
  before the harder-to-fully-control part of the system (the model)
  ever runs.

If anything here still feels unclear, ask before moving to Lesson 34.
