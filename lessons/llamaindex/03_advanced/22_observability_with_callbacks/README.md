# Lesson 22: Observability with Callbacks

## Every query so far has been a black box

`query_engine.query(question)` has been a one-line call for 21 lessons:
a `Response` comes back, and that's all you see. How many LLM calls did
that actually make? How many tokens did they use? What order did
retrieval, embedding, and synthesis happen in? None of that has been
visible, until now.

`llama_index.core.callbacks` answers those questions without changing a
single line of query code. A callback handler observes every internal
event (LLM calls, embedding calls, node parsing, retrieval, synthesis)
as it happens, and you attach handlers globally via
`Settings.callback_manager`, the same "set once on `Settings`, everything
built afterward picks it up automatically" pattern Lesson 3 introduced
for `Settings.llm` and `Settings.embed_model`.

## Two handlers, two different views of the same events

This lesson attaches both at once:

| Handler | What it captures |
|---|---|
| `TokenCountingHandler` | Cumulative token counts: embedding tokens, LLM prompt tokens, LLM completion tokens |
| `LlamaDebugHandler` | An ordered trace of every event type that fired, with timing |

`TokenCountingHandler` answers "how much did this cost," `LlamaDebugHandler`
answers "what actually happened, in what order." Both attach to the same
`CallbackManager`, which fans every event out to every handler registered
on it, they don't interfere with each other.

## The code, piece by piece

```python
token_counter = TokenCountingHandler()
llama_debug = LlamaDebugHandler(print_trace_on_end=False)
Settings.callback_manager = CallbackManager([token_counter, llama_debug])
```

`print_trace_on_end=False` disables `LlamaDebugHandler`'s default
behavior (auto-printing a trace tree every time a top-level operation
finishes), since this lesson prints its own summary instead, using
`get_event_pairs()` directly for a cleaner one-time view.

```python
token_counter.total_embedding_token_count
token_counter.prompt_llm_token_count
token_counter.completion_llm_token_count
token_counter.total_llm_token_count
```

All four counters are cumulative for as long as the handler stays
attached, they don't reset between calls. Note embedding tokens jump
twice in this lesson's output: once when the index is built (embedding
the 3 fixture documents), again during the query (embedding the
question itself).

```python
llama_debug.get_event_pairs()
```

Returns every recorded start/end event pair, in chronological order.
Each pair's `[0].event_type` names what kind of operation it was
(`EMBEDDING`, `RETRIEVE`, `SYNTHESIZE`, `LLM`, and more).

## Running it

```bash
uv run python lessons/llamaindex/03_advanced/22_observability_with_callbacks/lesson.py
```

## Expected output

Token counts are exact for a given input (no LLM wording variance in
counting itself), but will shift slightly if the LLM's answer wording
varies between runs (completion token count depends on the actual reply
length); the answer text itself and the exact numbers below are one real
captured run:

```
Index built. Token usage so far (embedding the 3 fixture documents):
  embedding tokens: 762

Q: What is Nimbus Robotics' policy on expense reports submitted late?
A: The provided context does not contain any information regarding the policy on expense reports submitted late.

Cumulative token usage after the query:
  embedding tokens: 774
  LLM prompt tokens: 674
  LLM completion tokens: 17
  LLM total tokens: 691

Event trace captured by LlamaDebugHandler:
  NODE_PARSING
  CHUNKING
  CHUNKING
  CHUNKING
  EMBEDDING
  QUERY
  RETRIEVE
  EMBEDDING
  SYNTHESIZE
  CHUNKING
  CHUNKING
  TEMPLATING
  LLM
```

Note the fixture data genuinely has no late-submission policy, so the
LLM correctly said so instead of guessing, the same faithful behavior
Lesson 18's `FaithfulnessEvaluator` checks for automatically.

The event trace shows the real pipeline behind one `.query()` call:
`NODE_PARSING`/`CHUNKING` (splitting documents into Nodes while building
the index) and the first `EMBEDDING` happen during `VectorStoreIndex.from_documents()`;
`QUERY` -> `RETRIEVE` -> a second `EMBEDDING` (the question) -> `SYNTHESIZE`
-> `CHUNKING`/`TEMPLATING`/`LLM` happen during the actual query, this is
the same retrieve-then-synthesize shape Lesson 19's hand-rolled Workflow
made explicit.

## Checkpoint

- **`Settings.callback_manager`**: a global hook point, set once, every
  Index and QueryEngine built afterward reports events to it
  automatically, no query code changes needed.
- **`TokenCountingHandler`**: cumulative embedding and LLM token counts,
  the "how much did this cost" view.
- **`LlamaDebugHandler`**: an ordered event trace with timing, the
  "what actually happened" view; `get_event_pairs()` reads it back
  programmatically.
- Both handlers attach to the same `CallbackManager` and observe the
  same underlying events without interfering with each other.

If anything here still feels unclear, ask before moving to Lesson 23.
