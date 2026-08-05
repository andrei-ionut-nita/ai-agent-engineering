# Lesson 25: Long-term memory with a store

## Two very different kinds of memory

Lessons 13 and 14's checkpointers remember everything within one
`thread_id`. That's exactly right for "what did we just discuss in this
conversation," but it has a hard edge: a brand new `thread_id` starts
completely blank, even if it's the same actual person coming back the
next day in a new session. `InMemoryStore` solves a different problem:
memory keyed by something more durable than a thread, here, a user id,
so a fact learned in one conversation is still known in a completely
different, later one.

## Creating the store

```python
store = InMemoryStore()
```

One store, shared across every thread and every user. It isn't attached
to `compile()` in this lesson (Lesson 34 does that), instead, the node
functions below close over this instance directly. That's simpler to
follow than relying on LangGraph's store-injection into node signatures,
and it's guaranteed to work the same way every time.

## Writing a fact

```python
def remember(state: MessagesState, user_id: str) -> dict:
    last_text = state["messages"][-1].content
    if "remember" in last_text.lower():
        store.put(("memories", user_id), "preference", {"text": last_text})
    return {}
```

`store.put(namespace, key, value)` takes a **namespace**, a tuple like
`("memories", "user-42")`, a **key** identifying this specific fact
within that namespace, and a **value**, any plain dictionary. The
namespace is what keeps different users' facts from colliding, even
though they all share the same `store` object.

## Reading facts back, from any thread

```python
def chatbot(state: MessagesState, user_id: str) -> dict:
    saved = store.search(("memories", user_id))
    context = "\n".join(item.value["text"] for item in saved)
    ...
```

`store.search(namespace)` returns every item saved under that namespace,
regardless of which `thread_id` wrote them. This lookup never mentions
`thread_id` at all, that's the whole point: it's keyed purely by
`user_id`, so it works the same whether this is the user's first message
ever or their hundredth conversation.

## Proving it crosses threads

```python
config_a = {"configurable": {"thread_id": "thread-a"}}
result1 = app.invoke({"messages": [HumanMessage("Please remember that I'm allergic to peanuts.")]}, config_a)

config_b = {"configurable": {"thread_id": "thread-b"}}
result2 = app.invoke({"messages": [HumanMessage("What allergy should the caterer know about?")]}, config_b)
```

`thread-a` and `thread-b` share no checkpointer history whatsoever, as
far as `InMemorySaver` would be concerned (there isn't even one attached
in this lesson), they're two unrelated conversations. Yet `thread-b`
correctly answers about the peanut allergy, because `store.search` in
the `chatbot` node looked it up by `user_id`, not `thread_id`.

## Running it

```bash
uv run python lessons/langgraph/03_advanced/25_long_term_memory_store/lesson.py
```

## Checkpoint

- **`InMemoryStore`**: cross-thread memory, keyed by namespace (e.g. a
  user id), separate from any checkpointer's per-thread memory.
- **`store.put(namespace, key, value)`**: saves a fact under a specific
  namespace and key.
- **`store.search(namespace)`**: retrieves everything saved under a
  namespace, from any thread.
- **checkpointer vs. store**: a checkpointer remembers one conversation;
  a store remembers a user (or any other durable identity) across every
  conversation they've ever had.

If anything here still feels unclear, ask before moving to Lesson 26.
