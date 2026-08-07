# Lesson 12: Multi-Turn Memory

## Models don't remember anything

This is worth saying plainly: `llama3.2` (or any model, local or
cloud) has no memory of your last call by the time you make a new one.
Every single call is stateless, it only ever sees what's in the
`messages` list you send *that time*. "Conversation memory" isn't a
feature the model has, it's a pattern you implement yourself: keep a
growing list, and resend the whole thing on every turn.

Lesson 9's checkpoint built a fresh `messages` list on every question,
which is why the assistant there couldn't have answered "what did I
just ask you?", it genuinely had no way to know. This lesson fixes
that by reusing one list across turns.

## The code, piece by piece

```python
messages: list[dict] = []
```

Declared once, outside the loop, and never replaced, only appended to.

```python
def turn(user_text: str) -> None:
    messages.append({"role": "user", "content": user_text})
    response = ollama.chat(model=MODEL, messages=messages, options={"temperature": 0})
    messages.append({"role": "assistant", "content": response.message.content})
```

Each call to `turn()` does three things: adds the new user message to
the running list, sends the *entire* list (not just the new message)
to `ollama.chat()`, then appends the model's own reply back onto the
same list. That last step is easy to forget and breaks everything if
you do: without the assistant's own words in the history, the model
has no record of what it already said, and can contradict or repeat
itself on the next turn.

```python
turn("My favorite color is teal. Remember that.")
turn("What is my favorite color?")
```

By the second call, `messages` holds four entries: the first
question, the first answer, the second question, and (about to be
added) the second answer. The model only "remembers" teal because that
fact is sitting right there in the list it was just sent, not because
of any memory on Ollama's side.

## The real cost of this pattern

Every additional turn means a longer `messages` list, which means more
tokens read on *every subsequent call*, even ones that don't need the
early history. A ten-turn conversation resends all nine prior turns
before generating the tenth answer. Lesson 19 covers what happens when
that list grows past a model's context window; production systems
often trim, summarize, or otherwise limit history rather than keeping
it unbounded forever.

## Running it

```bash
uv run python lessons/ollama/02_intermediate/12_multi_turn_memory/lesson.py
```

## Expected output

```
You: My favorite color is teal. Remember that.
Assistant: I've taken note that your favorite color is teal. I'll keep that in mind for our conversation. How can I assist you today?

You: What is my favorite color?
Assistant: I remember! Your favorite color is teal.

Full conversation so far has 4 messages.
  [user] My favorite color is teal. Remember that.
  [assistant] I've taken note that your favorite color is teal. I'll keep 
  [user] What is my favorite color?
  [assistant] I remember! Your favorite color is teal.
```

The exact assistant wording will vary between runs, but the second
answer should always correctly say "teal", that's the actual test:
proof the model used the earlier turn, not luck.

## Checkpoint

- **Models are stateless**: no call remembers a previous one on its
  own, memory is entirely a client-side pattern.
- **The growing `messages` list**: append the user's message, call the
  model, append the model's reply, repeat.
- **Forgetting to append the assistant's reply**: breaks memory, the
  model loses track of what it already said.
- **Cost**: every turn resends the whole history, longer conversations
  mean more tokens processed on every single call.

If anything here still feels unclear, ask before moving to Lesson 13.
