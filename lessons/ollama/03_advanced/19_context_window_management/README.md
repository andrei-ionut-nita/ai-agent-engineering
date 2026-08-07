# Lesson 19: Context Window Management

## The bill comes due eventually

Lesson 12 built real conversation memory by resending the entire
`messages` list on every turn, and warned that this list only grows.
This lesson shows what actually happens once it grows past what the
model can see at once: not a clean error, but silent, partial memory
loss.

## `num_ctx` and a model's real ceiling

```python
max_ctx = ollama.show("llama3.2").modelinfo["llama.context_length"]
```

Every model has a maximum context length it was trained to handle,
`llama3.2` supports up to 131,072 tokens. `num_ctx` (from Lesson 6)
lets you set a *smaller* working budget than that maximum, useful for
controlling memory usage, since a larger context window means more
RAM/VRAM reserved for it, whether or not a given conversation actually
needs that much. `num_ctx` can shrink the ceiling, it can never raise
it past what the model itself supports.

## What happens when the conversation doesn't fit

When a conversation's total token count exceeds `num_ctx`, something
has to give, and Ollama drops the oldest messages first to make room,
silently. No error, no warning in the response, the model simply never
sees the parts that got dropped.

```python
messages = [SECRET_INSTRUCTION] + <39 turns of generic filler> + [QUESTION]
```

The one piece of real information in this conversation, the secret
code word, is stated exactly once, in the very first message. With a
small `num_ctx`, that first message is exactly what gets pushed out to
make room for everything after it, so the model answers with only a
fragment it can still reconstruct from pattern (`"BANANA"`, missing
the `"77"`), not the real, complete instruction. With a large enough
`num_ctx`, nothing gets dropped, and the answer is correct and
complete.

## Why this matters for real agents

This is exactly the failure mode a long-running agent or chatbot hits
in production: an important instruction, fact, or user preference
stated early in a session quietly stops being visible to the model
once enough conversation piles up after it, and nothing in the API
tells you it happened. Real systems handle this by summarizing or
pruning older history deliberately (rather than letting truncation
happen blindly), or by moving durable facts into a system prompt that
gets re-sent fresh every turn instead of relying on it surviving deep
in history.

## Running it

```bash
uv run python lessons/ollama/03_advanced/19_context_window_management/lesson.py
```

## Expected output

```
Conversation has 80 messages, the secret is stated once, right at the start.

llama3.2's maximum supported context: 131072 tokens

num_ctx=512 (small): The secret code word is: BANANA
num_ctx=8192 (large): The secret code word is BANANA77.
```

With `temperature=0`, this should reproduce exactly. If your machine
handles the small `num_ctx` case slightly differently, the key
comparison to look for is still there: the small-context answer should
be visibly worse or incomplete compared to the large-context one.

## Checkpoint

- **`num_ctx`**: a working budget you can set below a model's real
  maximum, never above it.
- **What happens on overflow**: the oldest messages are silently
  dropped, no error, the model just never sees them.
- **Why it's dangerous**: information stated early in a long
  conversation can quietly vanish with no signal that it happened.
- **Mitigation**: summarize/prune history deliberately, or keep durable
  facts in a system prompt resent every turn rather than buried in
  history.

If anything here still feels unclear, ask before moving to Lesson 20.
