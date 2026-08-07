# Lesson 4: `generate()` vs `chat()`

## Two APIs, one model underneath

Lesson 3 used `ollama.generate()`, the simplest possible call: a flat
string in, a written answer out. Ollama also offers `ollama.chat()`,
which takes a list of role-tagged messages (`system`, `user`,
`assistant`) instead of one string, the same message shape you'll
recognize from LangChain's messages in the other courses.

Both APIs end up talking to the exact same model. The difference is
who's responsible for formatting the prompt correctly.

## Why chat template formatting matters

Lesson 2's `ollama.show()` printed a `template` field, a small program
(in Go's templating syntax) that wraps your text in special tokens
like `<|start_header_id|>system<|end_header_id|>` before the model
ever sees it. Every instruction-tuned model was fine-tuned to expect
its input wrapped exactly this way; get the wrapping wrong and answer
quality quietly degrades; the model doesn't error, it just performs
worse, in a way that's easy to miss.

`generate()` skips that template entirely unless you build the wrapping
yourself; `chat()` applies the model's own template automatically from
a plain list of messages. That's the whole reason `chat()` exists as a
separate method, not just a convenience wrapper.

## The code, piece by piece

```python
response = ollama.generate(
    model="llama3.2",
    prompt=f"You are a terse assistant. Answer in one sentence.\n\n{PROMPT}",
)
```

This hand-glues a system instruction onto the front of the prompt with
a newline. It often works well enough for small models, which is
exactly the trap: it looks fine in a quick test, but there's no
guarantee the model reliably distinguishes "instruction" from
"question" this way, especially as prompts get longer or more complex.

```python
response = ollama.chat(
    model="llama3.2",
    messages=[
        {"role": "system", "content": "You are a terse assistant. Answer in one sentence."},
        {"role": "user", "content": PROMPT},
    ],
)
response.message.content
```

`messages` is a list of plain dicts with `"role"` and `"content"` keys,
no special classes required. Ollama applies the model's chat template
to this list before sending anything to the model, so `system` really
is treated as an instruction, not just text that happens to come
first. The reply comes back as `response.message`, an object with its
own `.role` (always `"assistant"` for a reply) and `.content`.

From here on, every lesson in this course uses `chat()`, exactly like
every lesson in the langchain course uses message-based calls, not raw
string prompts.

## Running it

```bash
uv run python lessons/ollama/01_beginner/04_chat_vs_generate/lesson.py
```

## Expected output

```
generate() with a hand-glued system instruction:
  A REST API (Representational State of Resource) is an architectural style for designing networked applications, emphasizing simplicity, flexibility, and scalability.

chat() with a proper system message:
  A REST API (Representational State of Resource) is an architectural style for designing networked applications that uses standard HTTP methods to interact with resources over the web.
```

Both answers should be roughly one sentence here, since `llama3.2` is
good enough to follow the hand-glued instruction too, the gap between
the two approaches gets more visible with smaller models, longer
system prompts, or multi-turn conversations (Lesson 12). The exact
wording will vary between runs either way.

## Checkpoint

- **`generate()`**: one flat string in, no chat template applied for
  you, correctness of any system instruction is your own responsibility.
- **`chat()`**: a list of role-tagged messages, the model's own chat
  template applied automatically, matches how every other course in
  this repo structures a call.
- **Chat template**: a per-model wrapping (special tokens around
  roles) baked in during fine-tuning; getting it wrong degrades
  quality silently, not with an error.

If anything here still feels unclear, ask before moving to Lesson 5.
