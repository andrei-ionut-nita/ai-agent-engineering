# Lesson 34: Deploying a persistent agent, both kinds of memory at once

## What a real deployment actually needs

Lesson 14 gave a graph memory that survives a restart, per thread.
Lesson 25 gave a graph memory that crosses threads, per user. Neither
one replaces the other, they solve different problems: "what did we
discuss in this conversation" versus "what do I know about this person,
regardless of which conversation they're in." A real deployed agent
typically needs both running at the same time, on the same compiled
graph.

## Attaching both to one compile call

```python
return builder.compile(checkpointer=checkpointer, store=store)
```

`compile()` accepts both a `checkpointer` and a `store` as independent
keyword arguments. Neither one knows the other exists, they're separate
systems, doing separate jobs, that both happen to be available to every
node in this graph.

## The checkpointer half: durable, per-thread

```python
with SqliteSaver.from_conn_string(str(DB_PATH)) as checkpointer:
    app = build_app_for_user(user_id, checkpointer)
    ...
```

Exactly Lesson 14's pattern: a real `.sqlite` file on disk, opened as a
context manager. Every turn within one `thread_id` is remembered here,
and survives the program exiting and restarting, same as before.

## The store half: cross-thread, keyed by user

```python
store = InMemoryStore()

def chatbot(state: MessagesState) -> dict:
    saved = store.search(("profile", user_id))
    ...
```

Exactly Lesson 25's pattern: one store shared across every thread,
looked up by `user_id` rather than `thread_id`. Note this store is
`InMemoryStore`, still RAM-only in this lesson, a real deployment would
typically back the store with its own persistent storage too, the point
here is the two memory *systems* coexisting, not that both happen to be
durable in this specific demo.

## Proving both work together

```python
config_1 = {"configurable": {"thread_id": "support-session-1"}}
r2 = app.invoke({"messages": [HumanMessage("What did I just tell you?")]}, config_1)
# answered via the CHECKPOINTER, same thread as the previous turn

config_2 = {"configurable": {"thread_id": "support-session-2"}}
r3 = app.invoke({"messages": [HumanMessage("What account tier am I on?")]}, config_2)
# answered via the STORE, a brand new thread, same user
```

`config_1`'s second turn works because the checkpointer remembers turn
one, same thread. `config_2` is an entirely new thread with no
checkpointer history in common with `config_1` at all, yet it still
knows the account tier, because that fact came from the store, looked up
by `user_id`, completely independent of which thread asked.

## Running it

```bash
uv run python lessons/langgraph/03_advanced/34_deploying_persistent_agent/lesson.py
```

## Checkpoint

- **`compile(checkpointer=..., store=...)`**: both memory systems attach
  to the same compiled graph, independently of each other.
- **checkpointer**: durable, per-`thread_id`, this conversation's
  history.
- **store**: cross-thread, keyed by whatever identity you choose (a user
  id here), facts that follow the person, not the conversation.
- **why deployed agents need both**: users have both short conversations
  and a longer-lived identity; one memory system alone only covers half
  of that.

If anything here still feels unclear, ask before moving to Lesson 35,
the Advanced tier's capstone project, and the final lesson in this
course.
