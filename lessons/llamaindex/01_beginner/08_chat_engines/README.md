# Lesson 8: Chat engines and memory

## Adding memory on top of retrieve -> synthesize

Every `QueryEngine` call in Lessons 5-7 was stateless: `.query()` knew
nothing about any call before it, ask the same question twice and
you'd get the same retrieval and roughly the same answer both times.
`index.as_chat_engine()` wraps the same `Index` but adds a conversation
history the engine consults on every turn, so a follow-up like "what
about for existing employees?" can be understood without repeating
"vacation days" or "first 90 days" again.

| | QueryEngine (Lessons 5-7) | ChatEngine |
|---|---|---|
| Method | `.query(question)` | `.chat(message)` |
| Memory across calls | None, stateless | Yes, accumulates history on the engine object |
| Follow-ups needing prior context | Fail or misfire | Work |
| Underlying pipeline | retrieve -> synthesize | condense question (using history) -> retrieve -> synthesize |

## How `condense_question` mode works

The default chat mode first asks the LLM to rewrite the newest message
into a standalone question using the chat history, turning something
like "what about for existing employees?" into something closer to
"how much vacation can existing employees use after their first 90
days?" internally, THEN runs that rewritten question through the same
retrieve -> synthesize pipeline Lesson 5 used. This is why a
`ChatEngine` can answer a follow-up a plain `QueryEngine` can't:
history is folded into what actually gets *retrieved*, not just handed
to the LLM as extra text alongside an unrelated retrieval.

## The code, piece by piece

```python
chat_engine = index.as_chat_engine()
```

Builds a chat engine from the same `VectorStoreIndex` every prior
lesson in this section used.

```python
for message in turns:
    response = chat_engine.chat(message)
```

The same `chat_engine` object is reused across every iteration of this
loop, on purpose, `.chat()` mutates the engine's internal history, so
reusing one instance is what makes turn 2 aware of turn 1.

## Running it

```bash
uv run python lessons/llamaindex/01_beginner/08_chat_engines/lesson.py
```

## Expected output

All bot wording is LLM-generated and non-deterministic, this run's
tone happened to be chattier than earlier lessons; your exact phrasing
will vary, but the follow-ups should stay correctly on-topic the same
way. Captured from a real run:

```
Index built from 3 documents.

User: How many vacation days do new hires get to use in their first 90 days?
Bot:  ... new hires ... are restricted to using a maximum of 5 days of paid vacation during their first 90 days of employment ...

User: What about for existing employees, past their first 90 days?
Bot:  ... full-time employees accrue a total of 20 days of paid vacation per calendar year ... unused vacation days are allowed to roll over ... up to a maximum carryover cap of 10 days ...

User: And remind me, how many paid public holidays are there per year?
Bot:  ... the company observes 10 paid public holidays per year ...

query_engine.query() is stateless: no memory between calls (Lessons 5-7).
chat_engine.chat() is stateful: retains conversation history across calls.
```

(Full bot responses are printed when you actually run it, trimmed here
for length.) The key thing to verify when you run this yourself: turn
2's question never mentions "vacation" by name, "what about for
existing employees, past their first 90 days?", and the bot still
answers about vacation days specifically, not some other policy. That
only works because the engine's history carries turn 1's subject
forward.

## Checkpoint

- **`index.as_chat_engine()`**: wraps an `Index` with conversation
  memory on top of the same retrieve -> synthesize pipeline
  `QueryEngine` uses.
- **`.chat(message)`** is stateful: it reads and appends to the
  engine's internal history, unlike `.query()`, which is stateless.
- Reuse the same `ChatEngine` instance across a conversation, a new
  instance means no memory of prior turns.
- The default mode rewrites each new message into a standalone
  question using history before retrieving, which is why follow-ups
  that omit the original subject still retrieve the right Nodes.

If anything here still feels unclear, ask before moving to Lesson 9.
