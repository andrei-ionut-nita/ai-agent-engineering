# Lesson 9 (Checkpoint): Streaming Chatbot, Fully Offline

## What this combines

Nothing new here, this is where the beginner tier's pieces meet:

- **`chat()` with a system message** (Lesson 4): a persona set once,
  applied to every question.
- **Streaming** (Lesson 5): each answer prints as it's generated,
  instead of appearing all at once.
- **`options={"temperature": 0.3}`** (Lesson 6): a lower, fixed
  temperature, appropriate for a factual Q&A assistant rather than a
  creative one.

And, underneath all of it, the theme of Lessons 1-3: no `.env`, no
API key, no internet required at any point. If you want proof, turn
off your network connection and run this again, it'll work identically.

## The design

`ask()` wraps a single question in a fresh `messages` list every time,
the same `SYSTEM_PROMPT` repeated on each call rather than accumulated
conversation history. That's intentional here: real multi-turn memory,
where the assistant remembers *earlier* answers in the same
conversation, is Lesson 12's job, not this checkpoint's. Each question
in this lesson is answered independently.

```python
def ask(question: str) -> str:
    stream = ollama.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        stream=True,
        options={"temperature": 0.3},
    )
```

`main()` just loops over three fixed questions and calls `ask()` on
each, printing "You:" and "Assistant:" labels to make the transcript
read like an actual conversation, even though each turn is technically
a fresh, independent call.

## Running it

```bash
uv run python lessons/ollama/01_beginner/09_beginner_checkpoint_project/lesson.py
```

Watch the terminal while it runs, each answer should visibly stream in
rather than appear all at once.

## Expected output

```
System prompt: You are a concise, friendly local assistant. Answer in two sentences or fewer.

You: What is Python primarily used for?
Assistant: Python is a versatile language primarily used for web development, data analysis, artificial intelligence, and machine learning. Its simplicity and extensive libraries make it a popular choice for beginners and experts alike.

You: Name the largest planet in the solar system.
Assistant: The largest planet in our solar system is Jupiter. It's a gas giant with a diameter of approximately 142,984 kilometers (88,846 miles).

You: Give one tip for writing clean code.
Assistant: One tip for writing clean code is to follow the Single Responsibility Principle (SRP), where each function or module has only one reason to change. This helps maintain code organization and reduces the likelihood of bugs and errors.
```

The exact wording will vary between runs (this is a real model
answering freely, low temperature makes it steadier, not identical),
but each answer should stay close to two sentences, honoring the
system prompt.

## Checkpoint

If this lesson ran cleanly and made sense without looking anything up,
you're ready for the intermediate tier. You should be able to explain,
in your own words:

- Why `ollama.chat()` is preferred over `ollama.generate()` once a
  system prompt is involved (Lesson 4).
- What `stream=True` changes about the return value, and why it
  matters for a real user (Lesson 5).
- What `temperature` and `seed` each control, and why they're
  different knobs (Lesson 6).
- The difference between `ollama.list()` (on disk) and `ollama.ps()`
  (in memory) (Lesson 7).
- Why an embedding model like `nomic-embed-text` can't answer
  questions the way `llama3.2` does (Lesson 8).

If any of those feel shaky, it's worth a quick re-read of that lesson
before continuing, everything from here builds on this tier directly.
