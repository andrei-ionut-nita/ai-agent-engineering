# Lesson 30: Human-in-the-loop, pausing before a risky action

## Why this matters

Every tool so far has been harmless: a calculator, a word counter, a
document search. Real agents sometimes need tools that do things you
can't take back, sending an email, charging a card, deleting a file.
For those, you often want a human to see and approve the exact action
*before* it happens, not just review it after the fact. This lesson
builds that pause point.

## A tool standing in for something risky

```python
@tool
def send_email(to: str, body: str) -> str:
    """Send an email to someone."""
    return f"Email sent to {to}: {body}"
```

Same `@tool` pattern as always. What's different is the *stakes*: once
this runs, an email has gone out, there's no undo. Compare this to
Lesson 13's calculator, running it twice by mistake is harmless, running
`send_email` twice by mistake sends two emails.

## Pausing before the tool runs

```python
agent = create_agent(
    model=model,
    tools=[send_email],
    checkpointer=InMemorySaver(),
    interrupt_before=["tools"],
)
```

`interrupt_before=["tools"]` tells the agent's internal graph to stop
right before entering its `"tools"` step, every time, regardless of
which tool was requested or with what arguments. A `checkpointer` is
required for this to work, pausing and resuming later only makes sense
if the agent's in-progress state is actually saved somewhere in the
meantime, the exact same `InMemorySaver` from Lesson 24, now serving a
second purpose beyond conversation memory.

## What happens when you call `.invoke()` now

```python
result = agent.invoke({"messages": [HumanMessage(question)]}, config)
last_message = result["messages"][-1]
```

This call returns *before* the tool actually runs. `last_message` is the
model's request to call a tool, exactly like `ai_message` in Lesson 14,
but this time nothing has executed yet, the agent stopped and is
waiting.

## Approving: resuming with `None`

```python
final = agent.invoke(None, config)
```

Passing `None` as the input, with the same `config` (same `thread_id`),
means "continue from exactly where you paused." The agent picks back up
right where it left off, actually runs the tool this time, and finishes
normally. Run the lesson and you'll see the approved email genuinely get
"sent."

## Rejecting: simply never resuming

```python
else:
    print("   -> rejected, tool was never run.")
```

There's no special "reject" method to call. Rejecting is just... not
calling `agent.invoke(None, config)`. The agent stays paused forever (or
until you resume it), the tool never runs, nothing happens. Run the
lesson's second example (the layoffs email) and confirm no email
message is ever printed, the pause was the last thing that happened for
that thread.

## Why this generalizes beyond email

The pattern here, pause before something irreversible, show a human the
exact request, only proceed on approval, is the same shape whether the
risky action is sending an email, running a database migration, making
a payment, or posting publicly on someone's behalf. `interrupt_before`
doesn't know or care what the tool does, it just guarantees a stopping
point exists before any tool call, which is exactly the right place to
put a human in control of consequential actions.

## Running it

```bash
uv run python lessons/langchain/03_advanced/30_human_in_the_loop/lesson.py
```

## Checkpoint

- **`interrupt_before=["tools"]`**: pauses the agent right before
  running any tool, requires a checkpointer to work.
- **resuming**: `agent.invoke(None, config)` with the same `thread_id`
  continues exactly where the agent paused.
- **rejecting**: simply never resuming, no special call needed, the
  tool just never runs.
- **when to use this**: any tool whose effects are hard or impossible to
  undo.

If anything here still feels unclear, ask before moving to Lesson 31.
