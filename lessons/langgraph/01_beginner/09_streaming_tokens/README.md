# Lesson 9: Streaming model tokens out of a node

## Where we left off

Lesson 8 streamed whole node outputs, useful for watching a
multi-node pipeline progress, but each chunk still only appeared once
an entire node had finished, including any model call inside it. If a
node's model call takes a few seconds to write a long answer, "values"
and "updates" streaming still make you wait for all of it before that
node's chunk shows up. `stream_mode="messages"` fixes that by streaming
the model's reply token by token, from inside a node, as the words are
actually generated.

## What we're building

Lesson 6's single model-call graph, unchanged, streamed with
`stream_mode="messages"` so the answer prints as it's written instead of
all at once at the end.

## The code, piece by piece

```python
for token_chunk, metadata in app.stream(
    {"messages": [HumanMessage("Explain graphs in three short sentences.")]},
    stream_mode="messages",
):
    print(token_chunk.text, end="", flush=True)
```

`stream_mode="messages"` yields a `(token_chunk, metadata)` tuple for
every small piece of output the model produces internally, this is the
same token-by-token streaming a chat UI shows you. `token_chunk` is a
message chunk (a partial `AIMessageChunk`, holding just that piece of
text), `.text` gives you the piece of text itself. `metadata` is a
dictionary telling you which node and which model call this token came
from, useful once a graph has more than one node that talks to a model
and you want to tell their outputs apart.

`end="", flush=True` on `print` matters here: without `end=""`, every
token would print on its own line. `flush=True` forces each piece to
show up immediately instead of Python buffering several tokens before
displaying them, which would defeat the purpose of streaming.

## Why this is a different mode, not just "updates" again

`"values"` and `"updates"` (Lesson 8) both operate at the granularity of
whole node outputs, a node either has finished or it hasn't, there's no
in-between. `"messages"` reaches inside a node's model call itself and
streams pieces of that call's output as they're generated, which is a
finer granularity than "a node finished." A graph can use all three
modes depending on what you're building: `"updates"` to log progress
across nodes, `"messages"` to show one particular node's answer arriving
live.

## Running it

```bash
uv run python lessons/langgraph/01_beginner/09_streaming_tokens/lesson.py
```

You should see the answer appear gradually in your terminal, piece by
piece, rather than all at once.

## Checkpoint

- **`stream_mode="messages"`**: streams token-level chunks from any
  model call inside a node, as they're generated.
- **`(token_chunk, metadata)`**: each streamed item is a pair, the piece
  of the message and info about which node/call produced it.
- **finer granularity than `"values"`/`"updates"`**: those stream once
  per finished node, `"messages"` streams multiple times per model call
  within a single node.

If anything here still feels unclear, ask before moving to Lesson 10.
