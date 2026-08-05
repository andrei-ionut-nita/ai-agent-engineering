# Lesson 28: Trimming context inside a node

## The problem a loop eventually creates

Any graph with a loop (Beginner Lesson 5's shape) that keeps appending
to `state["messages"]` will, given enough iterations, eventually hand
the model more text than it can accept, or simply more than makes sense
to pay for. `trim_messages` (the same utility the langchain course used
at the top level, langchain course lesson 25) solves this from inside a
node: shrink what actually gets sent to the model, without touching what
state itself remembers.

## Trimming before the model call

```python
trimmed = trim_messages(
    full_history,
    max_tokens=4,
    token_counter=len,
    strategy="last",
    include_system=False,
)
response = model.invoke([system, *trimmed])
```

`trim_messages` takes a list of messages and a budget, `max_tokens`. The
`token_counter` decides how that budget is measured, here it's just
`len`, so each message counts as one unit, keeping the demo easy to
follow. `strategy="last"` keeps the most recent messages and drops older
ones first, the natural choice for a running conversation.

Crucially, this happens on a **local variable**, `trimmed`, built fresh
inside the node each time. `state["messages"]` itself is never modified,
the full history is still there, growing every iteration, we're only
shrinking what one specific model call gets to see.

## Why the node feeds a system instruction too

```python
system = SystemMessage("Answer only the latest question, in one short sentence. Do not recap prior facts.")
```

A subtlety worth noticing: a chatty model tends to restate earlier facts
in its own replies ("Nice to meet you, Alex from Denver..."), and since
those replies also live in the message history, restated facts can sneak
back into the trimmed window even after the original message that
introduced them is gone. Keeping replies terse removes that
self-reinforcing loop, so the trimming's actual effect is easy to see.

## The loop that accumulates messages

```python
def should_continue(state: MessagesState) -> str:
    answered = len([m for m in state["messages"] if isinstance(m, HumanMessage)])
    return "chatbot" if answered < len(QUESTIONS) else END
```

Same conditional-edge-back-to-itself shape as Lesson 5, run once per
canned question in `QUESTIONS`, so by the final iteration,
`state["messages"]` holds well over a dozen entries, even though the
model only ever sees the last handful of them on any single call.

## Running it

```bash
uv run python lessons/langgraph/03_advanced/28_context_trimming_in_a_node/lesson.py
```

The last question asks "What is my name?", after several facts have been
introduced and the window has scrolled past the message that named it.
Watch the final answer, and compare it against the total message count
printed at the end.

## Checkpoint

- **`trim_messages`**: shrinks what gets sent to the model, without
  modifying the state it was trimmed from.
- **`max_tokens` + `token_counter`**: together define the budget and how
  it's measured, here, message count for simplicity.
- **`strategy="last"`**: keeps the most recent messages, drops the
  oldest first.
- **state keeps everything, the model doesn't see everything**: the two
  are deliberately decoupled, so you can always inspect full history
  even while feeding the model a bounded slice of it.

If anything here still feels unclear, ask before moving to Lesson 29.
