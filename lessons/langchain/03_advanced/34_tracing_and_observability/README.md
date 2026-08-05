# Lesson 34: Tracing and observability

## What we've been missing this whole course

Every lesson has only ever shown you the *final* answer. When an agent
uses tools (Lessons 14 onward), a lot happens in between: the model
gets called, decides to use a tool, the tool runs, the model gets
called again. We've occasionally printed pieces of this manually (like
`tool_calls` in Lesson 14), but there's never been an automatic,
general way to see every step. That's what **observability** means
here: being able to see what a system actually did, not just what it
concluded.

## A callback handler: code LangChain calls for you, automatically

```python
class TracingHandler(BaseCallbackHandler):
    def on_chat_model_start(self, serialized, messages, *, run_id, **kwargs) -> None:
        ...
    def on_llm_end(self, response, *, run_id, **kwargs) -> None:
        ...
    def on_tool_start(self, serialized, input_str, *, run_id, **kwargs) -> None:
        ...
    def on_tool_end(self, output, *, run_id, **kwargs) -> None:
        ...
```

`BaseCallbackHandler` defines a bunch of methods, `on_chat_model_start`,
`on_tool_end`, and many more, that do nothing by default. Subclassing it
and overriding the ones you care about means LangChain will call *your*
code automatically, at exactly those moments, without you having to
insert print statements throughout an agent's internal loop yourself.
This is the same idea as Lesson 33's middleware, hooking into specific
points in the agent's execution, but callbacks are specifically for
*observing*, not for changing what happens.

## Timing each step

```python
def on_chat_model_start(self, serialized, messages, *, run_id, **kwargs) -> None:
    self._start_times[str(run_id)] = time.time()
    ...

def on_llm_end(self, response, *, run_id, **kwargs) -> None:
    elapsed = time.time() - self._start_times.get(str(run_id), time.time())
    print(f"[model call finished] took {elapsed:.2f}s")
```

Each step gets a `run_id`, a unique identifier for that specific call.
Recording the start time when a step *starts*, keyed by its `run_id`,
and computing the elapsed time when it *ends*, lets you time each
individual model call and tool call separately, even if several
overlap (which can happen with more advanced, concurrent agent setups).

## Attaching the handler

```python
result = agent.invoke(
    {"messages": [HumanMessage("How many letters are in the word 'observability'?")]},
    config={"callbacks": [tracer]},
)
```

`config={"callbacks": [...]}` is the same `config` parameter you've
passed before (recall the `thread_id` config in Lessons 24 and 30), just
carrying a different kind of instruction this time: "call these
handlers at every relevant step during this run."

## Reading the trace

Run the lesson and you'll see something like:

```
[model call started]  (1 messages in context)
[model call finished] took 0.44s
[tool started]  get_word_length({'word': 'observability'})
[tool finished] took 0.00s -> 13
[model call started]  (3 messages in context)
[model call finished] took 0.36s

Final answer: There are 13 letters in the word 'observability'.
```

This is the exact same three-round loop from Lesson 14 (ask, run a
tool, ask again), now fully visible: two separate model calls, one
tool call in between, each with its own timing, all without changing
anything about the agent itself, or writing debug prints inside its
tool-call loop by hand.

## Why this matters beyond curiosity

For a small demo, printing this is mostly interesting. For a real
application, this exact mechanism is how you'd debug why an agent chose
a certain tool, notice a tool call that's taking unexpectedly long, or
measure how much of your total response time is spent thinking (model
calls) versus doing (tool calls). Production systems typically send
this same kind of trace data to a dedicated observability platform
(like LangSmith, LangChain's own) rather than printing it to the
console, but the underlying mechanism, callback handlers hooking into
specific execution points, is identical.

## Running it

```bash
uv run python lessons/langchain/03_advanced/34_tracing_and_observability/lesson.py
```

## Checkpoint

- **observability**: being able to see what a system actually did
  internally, not just its final output.
- **`BaseCallbackHandler`**: a class you subclass and override specific
  `on_*` methods on, called automatically by LangChain at matching
  execution points.
- **`run_id`**: uniquely identifies one specific step, letting you match
  its start and end even when multiple steps could overlap.
- **`config={"callbacks": [...]}`**: attaches handlers to a specific
  `.invoke()` call.

If anything here still feels unclear, ask before moving to Lesson 35,
the Advanced tier's capstone project, and the final lesson in this
course.
