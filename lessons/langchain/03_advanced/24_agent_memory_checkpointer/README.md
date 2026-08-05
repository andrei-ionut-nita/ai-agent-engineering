# Lesson 24: Giving the agent real memory

## Where we left off

Lesson 23 built an agent that automates the tool-call loop, but each
`.invoke()` was still independent, no memory across calls. This lesson
adds a **checkpointer**, so the agent remembers earlier turns
automatically.

## The checkpointer: real memory, not a list you manage

```python
checkpointer=InMemorySaver()
```

In Lesson 17, `history` was a plain Python list, living only inside our
running program, and we were responsible for appending to it and
resending it every single time. A checkpointer does that same job, but
automatically, and it's built to eventually save to a real database (so
it survives your program restarting) instead of always living in
memory.

`InMemorySaver` is the simplest version, it still forgets everything
when the program ends, same limitation as Lesson 17, but the mechanism
is now something a real production agent would just swap out for a
persistent one (covered in Lesson 32), without changing any other code.

```python
config = {"configurable": {"thread_id": "lesson-24-demo"}}
...
result = agent.invoke({"messages": [HumanMessage(user_input)]}, config)
```

`thread_id` is the key idea here. It's like a conversation ID. Every
`.invoke()` call tagged with the same `thread_id` shares the same
remembered history behind the scenes, the checkpointer looks up
everything that happened before under that ID, and prepends it, before
the agent ever sees your new message. Change the `thread_id`, and you'd
get a completely fresh, unrelated conversation, even reusing the exact
same `agent` object.

This is how a real app serves memory correctly for many different users
or conversations at once, using one agent, distinguishing them purely
by thread ID.

Notice what we send each turn now:

```python
agent.invoke({"messages": [HumanMessage(user_input)]}, config)
```

Just the new message. Not the whole history, unlike Lesson 17. The
checkpointer already has everything earlier, tagged under this
`thread_id`.

## Running it

```bash
uv run python lessons/langchain/03_advanced/24_agent_memory_checkpointer/lesson.py
```

Try this conversation:

```
You: My favorite number is 7. What is it times 9?
Agent: 7 times 9 is 63!

You: What is my favorite number?
Agent: Your favorite number is 7!
```

Notice two things happened automatically, that we previously did by
hand: the first question needed the calculator (exact math, not a
guess), and the second question needed memory (recalling "7" from
earlier), and we didn't write a single line of tool-loop or
history-management code to make either happen.

## What this project has built up to, so far

| Lesson | What it added |
| ------ | -------------- |
| 1      | Sending one message to an AI, reading the reply |
| 3      | Reusable prompt templates |
| 6      | Chaining steps with `\|` |
| 13-14  | Defining a tool, and the manual ask/run/ask loop |
| 17     | Memory, understood as resending the whole conversation |
| 23-24  | `create_agent` automating both the tool loop and memory |

If any part of this lesson feels like magic, that's usually a sign it's
worth going back to the earlier lesson where that exact mechanism was
built by hand.

## Checkpoint

- **checkpointer**: automatic conversation memory, keyed by `thread_id`,
  replacing the manual list from Lesson 17.
- **`thread_id`**: identifies which ongoing conversation a given
  `.invoke()` call belongs to, so one agent can serve many separate
  conversations correctly.
- **`InMemorySaver`**: the simplest checkpointer, memory still lost when
  the program ends, swappable later for a persistent one.

If anything here still feels unclear, ask before moving to Lesson 25.
