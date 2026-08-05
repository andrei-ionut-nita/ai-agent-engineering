# Lesson 13: InMemorySaver, giving a graph real memory across calls

## Where we left off

Lesson 6 put a model inside a node. Lesson 7 gave that node tools. But
every `.invoke()` in the beginner tier was still independent, whatever
messages you passed in were the only ones the graph ever saw. Ask a
follow-up question in a second call, and the graph has no idea a first
call ever happened. This lesson fixes that with a **checkpointer**.

## The checkpointer: automatic memory, not a list you manage

```python
app = builder.compile(checkpointer=InMemorySaver())
```

That's the only structural change from a Lesson 6 style graph. A
checkpointer saves a snapshot of the graph's state after every node
finishes running, and it saves each snapshot under a **thread ID**, so
many separate conversations can share one compiled graph without
crosstalk. `InMemorySaver` is the simplest kind: snapshots live in this
process's RAM, and are gone the instant the program exits (Lesson 14
swaps this for a version that survives a restart).

## thread_id: which conversation is this?

```python
config_a = {"configurable": {"thread_id": "conversation-a"}}

result1 = app.invoke({"messages": [HumanMessage("My favorite color is teal.")]}, config_a)
result2 = app.invoke({"messages": [HumanMessage("What is my favorite color?")]}, config_a)
```

Both calls pass `config_a`, same `thread_id`. Before `chatbot` runs on
the second call, the checkpointer looks up everything saved earlier
under `"conversation-a"` and prepends it to state, so the model sees
the full conversation, not just the new question. Notice each call only
sends the *new* message, exactly like `create_agent` plus `InMemorySaver`
in the langchain course's Lesson 24, except here there's no
`create_agent` doing it for us, the checkpointer is doing this directly
against our own hand-built graph.

## A different thread_id is a different conversation

```python
config_b = {"configurable": {"thread_id": "conversation-b"}}
result3 = app.invoke({"messages": [HumanMessage("What is my favorite color?")]}, config_b)
```

Same compiled `app`, same process, same everything except the
`thread_id`. The model correctly has no idea what color was mentioned,
because `"conversation-b"` has no saved history yet. This is how one
compiled graph serves many independent users or sessions at once,
memory scoping is entirely a function of `thread_id`, not of which
Python object you're holding.

## Running it

```bash
uv run python lessons/langgraph/02_intermediate/13_checkpointer_memory/lesson.py
```

You should see the model recall "teal" on turn 2, and correctly deny
knowing any favorite color on turn 3, under the fresh thread.

## Checkpoint

- **checkpointer**: saves a snapshot of graph state after each node
  runs, keyed by `thread_id`, so `.invoke()` calls can share memory
  automatically instead of you resending the whole conversation.
- **`InMemorySaver`**: the simplest checkpointer, snapshots live only in
  this process's RAM, lost when the program exits.
- **`thread_id`**: identifies which conversation a call belongs to; same
  ID shares memory, a different ID starts fresh, even on the same
  compiled graph.
- **only send what's new**: with a checkpointer attached, each
  `.invoke()` only needs the newest message, not the full history.

If anything here still feels unclear, ask before moving to Lesson 14,
where this same memory is made to survive a program restart.
