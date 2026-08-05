# Lesson 25: Context trimming, keeping conversations within limits

## The problem, from Lesson 17

Lesson 17 established how memory actually works: every message ever
sent gets resent, in full, on every future turn. It also flagged a real
consequence: models can only read so much text in one request (their
**context window**), and a long enough conversation eventually exceeds
it. This lesson introduces one real strategy for handling that:
**trimming**, deliberately dropping older messages to stay under a
limit.

## `trim_messages`

```python
trimmed = trim_messages(
    long_history,
    max_tokens=60,
    token_counter=model,
    strategy="last",
    include_system=True,
)
```

- **`max_tokens=60`**: the budget. `trim_messages` keeps adding messages
  until adding one more would exceed this many tokens, then stops.
- **`token_counter=model`**: how to actually measure a message's size in
  tokens. Passing the model itself lets `trim_messages` use that
  specific model's own tokenizer, the most accurate option, since
  different models can count tokens slightly differently for the same
  text.
- **`strategy="last"`**: when something has to be cut, keep the most
  *recent* messages and drop the oldest ones first. (`strategy="first"`
  would do the opposite, keep the oldest, drop the newest, rarely what
  you want for a conversation.)
- **`include_system=True`**: always keep the `SystemMessage`, even
  though it's chronologically the very first message and would
  otherwise be among the first things dropped. Standing instructions are
  usually worth preserving no matter how much else gets trimmed.

## What actually happened

The lesson builds an 11-message conversation covering five unrelated
topics (a dog's name, a favorite food, learning violin, where someone
lives, a favorite color), oldest first. After trimming to a 60-token
budget, only 6 messages survive, the system message plus the most
*recent* few exchanges. The earliest topics (the dog's name, the
favorite food) are gone entirely.

## Proof it actually matters

```python
recent_question = trimmed + [HumanMessage("What is my favorite color?")]
old_question = trimmed + [HumanMessage("What is my dog's name?")]
```

Asking about the favorite color (mentioned near the end, likely
survived trimming) gets answered correctly. Asking about the dog's name
(mentioned at the very start, likely trimmed away) gets an honest "I
don't know", not a wrong guess, an admission that the information simply
isn't in what the model was given anymore.

This is the real tradeoff trimming makes: conversations can run
indefinitely without ever exceeding the context window, at the cost of
genuinely, permanently forgetting whatever got trimmed away. It's not
lying or hallucinating when it says it doesn't know, the information is
actually just gone from what it can see. Lesson 26 covers a different
strategy, summarizing old messages instead of dropping them outright,
that keeps a compressed trace of old information instead of losing it
completely.

## Running it

```bash
uv run python lessons/langchain/03_advanced/25_context_trimming/lesson.py
```

## Checkpoint

- **context window**: the limit on how much text a model can read in
  one request; long conversations eventually exceed it.
- **`trim_messages`**: cuts a message list down to fit a token budget.
- **`strategy="last"`**: keeps the most recent messages, drops the
  oldest first.
- **`include_system=True`**: keeps standing instructions regardless of
  how old they are chronologically.
- **the real tradeoff**: trimming genuinely forgets old information, it
  doesn't hide it or summarize it, it's simply no longer there.

If anything here still feels unclear, ask before moving to Lesson 26.
