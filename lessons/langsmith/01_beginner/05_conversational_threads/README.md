# Lesson 5: Grouping multi-turn runs into a conversation thread

## What we're building

A two-turn chat, each turn its own separate `chat_turn(...)` call and
therefore its own separate top-level run, tagged with the same
`thread_id` so LangSmith's UI can group them into one conversation
view instead of showing two unrelated runs. The model is given the
accumulated message history on each turn, so it genuinely remembers the
first turn when answering the second, not just something LangSmith
displays as connected.

## What this reveals

Lesson 2 showed nesting: runs called from inside other runs become
children automatically. Threads are a different relationship: two runs
that are **not** nested (each is its own top-level call, made at a
different time) but that belong to the same conversation. LangSmith
can't infer that connection from the call stack, there isn't one, so it
looks for a specific piece of metadata instead: `thread_id`. Any runs
sharing the same `thread_id` value show up grouped together in the
Threads view.

The one wrinkle is that `thread_id` has to be attached in two places at
once here, because two separate traced things are happening per turn:
`chat_turn` itself (a `@traceable` function) and the nested Gemini call
LangChain makes inside it. Each has its own way to receive metadata,
`langsmith_extra` for the manually-traced function, `config` for the
LangChain call, but the value carried is the same.

Grouping runs into a thread and the model actually remembering earlier
turns are two independent things, easy to conflate. `thread_id` alone
only affects how the UI displays runs, it does nothing to the model's
behavior. What makes the second answer coherent is that `chat_turn`
receives the full accumulated `history`, not just the latest message,
and passes all of it to `model.invoke()`. Without that, `thread_id`
would still group the two runs visually, but the model would answer the
second question with no memory of the first, since nothing about
`thread_id` feeds information back into the model itself.

## The code, piece by piece

```python
response = model.invoke(history, config={"metadata": {"thread_id": conversation_id}})
```

LangChain's `config` dict is how you attach metadata to a single
`.invoke()` call. It flows into the nested "llm" run that this call
produces (the same mechanism as Lesson 3's metadata on `answer_question`,
just passed through LangChain's own config system instead of directly
to `@traceable`).

```python
history.append(HumanMessage(message))
reply = chat_turn(
    conversation_id,
    history,
    langsmith_extra={"metadata": {"thread_id": conversation_id}},
)
history.append(("ai", reply))
```

`langsmith_extra` is accepted by every `@traceable`-wrapped function as
an extra keyword argument at call time, separate from the function's
declared parameters. It attaches metadata to that one run of `chat_turn`
without changing `chat_turn`'s own signature.

```python
conversation_id = str(uuid.uuid4())
```

A fresh, random id per script run, so running this lesson twice
produces two separate threads in the UI instead of one thread that
mixes runs from different runs of the script.

## Running it

```bash
uv run python lessons/langsmith/01_beginner/05_conversational_threads/lesson.py
```

In the UI, open the Threads view (or filter runs by the `thread_id`
metadata value printed... actually not printed, but visible on either
run's metadata panel) and confirm both turns appear together, in order.

## Checkpoint

- **Thread**: a group of runs that belong to the same conversation but
  aren't nested, connected only by a shared `metadata.thread_id` value.
- **Thread grouping is display-only**: `thread_id` affects what the UI
  shows you, not what the model remembers, actual memory requires
  passing accumulated history into each call yourself.
- **`langsmith_extra`**: a call-time keyword argument every `@traceable`
  function accepts, for attaching metadata/tags to one specific run
  without touching the function's real parameters.
- **`config={"metadata": ...}`**: how a LangChain `.invoke()` call
  attaches metadata to the run it produces.

If anything here still feels unclear, ask before moving to Lesson 6.
