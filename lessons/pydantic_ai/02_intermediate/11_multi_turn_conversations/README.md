# Lesson 11: Multi-turn conversations with `message_history`

## Agents don't remember anything by default

Each `run_sync` call is independent, the agent has no memory of a
previous call unless you give it one. This is the same statelessness
you saw in the `langchain` course: a model call is a pure function of
the messages you send it, nothing is remembered server-side.

## Carrying history forward

Every `AgentRunResult` exposes `new_messages()` (just the messages
produced by that run) and `all_messages()` (the full history including
whatever was passed in). Pass either into the next call's
`message_history=` to continue the conversation:

```python
result_1 = agent.run_sync("My favorite color is teal. Remember that.")

result_2 = agent.run_sync(
    "What is my favorite color?",
    message_history=result_1.new_messages(),
)
print(result_2.output)  # "Your favorite color is teal!"
```

`message_history` accepts `ModelMessage` objects, the same typed
representation of a request/response pair the SDK builds internally,
you're not hand-assembling role/content dicts the way you might with a
raw chat completions API.

## Building a conversation loop

In practice, you keep accumulating history across turns:

```python
history = []
for user_input in conversation:
    result = agent.run_sync(user_input, message_history=history)
    history = result.all_messages()
```

Reassigning `history = result.all_messages()` each turn (rather than
`new_messages()`) is what keeps the whole conversation, not just the
latest exchange, in context for the next call. This is the direct
equivalent of managing a growing list of `HumanMessage`/`AIMessage`
objects yourself in LangChain, just with the accumulation done for you
by `all_messages()`.

## Running it

```bash
uv run python lessons/pydantic_ai/02_intermediate/11_multi_turn_conversations/lesson.py
```

## Checkpoint

- `run_sync` calls are stateless by default; nothing carries over
  unless you pass `message_history=`.
- `result.new_messages()` is just this turn's messages;
  `result.all_messages()` is the whole history so far.
- A conversation loop reassigns `history = result.all_messages()` after
  every turn to keep the full context.

If anything here still feels unclear, ask before moving to Lesson 12,
where an agent calls another agent as a tool.
