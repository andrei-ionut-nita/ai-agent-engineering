# Lesson 3: Send one prompt, get one answer back

## What we're building

The local-model version of what langchain Lesson 1 did with Gemini:
one prompt in, one written answer out. No conversation history yet
(Lesson 12), no streaming (Lesson 5), just the smallest possible round
trip to a model running on your own machine.

## No API key, because there's no API to authenticate against

Every Gemini lesson in this repo starts with `load_dotenv()` and a
`GOOGLE_API_KEY`, because Google needs to know who's calling and
enforce a quota. Ollama has no such concept: the server it's talking
to is `http://localhost:11434`, a program running on your own
computer, not a company's infrastructure. There's nothing to prove and
no quota to hit (only your own hardware's limits).

## The code, piece by piece

```python
import ollama
```

Same client as Lessons 1 and 2, no setup beyond that import.

```python
response = ollama.generate(
    model="llama3.2",
    prompt="In one sentence, what is Python used for?",
)
```

`ollama.generate()` is the simplest possible call: a model name and a
raw prompt string, no message roles or conversation structure (that's
`ollama.chat()`, covered in Lesson 4 with the actual difference between
the two). This is a **blocking call**, exactly like LangChain's
`.invoke()`: your program pauses here until the model finishes writing
its full answer.

```python
response.response
```

The written answer itself. Unlike LangChain's `.text` property, this
is a plain attribute on a `GenerateResponse` object, note the name
collision, `response` is both the variable name and the attribute that
holds the text; `response.response` reads oddly but is correct.

```python
response.eval_count
response.prompt_eval_count
```

Local models report their own token accounting directly: `eval_count`
is how many tokens the model generated, `prompt_eval_count` is how
many it read from your prompt first. This is the same kind of
metadata Gemini's `AIMessage` carries, just under different attribute
names, since there's no per-token billing to justify hiding it behind
a "usage" object.

## Running it

```bash
uv run python lessons/ollama/01_beginner/03_first_generate_call/lesson.py
```

The first run against a given model can take a few extra seconds while
Ollama loads the model's weights into memory; after that, the model
usually stays loaded for a few minutes, so a second run right after
will be noticeably faster.

## Expected output

```
Python is a versatile and widely-used programming language that is used for a variety of purposes, including web development, data analysis, machine learning, automation, and more, thanks to its simplicity, flexibility, and extensive libraries.

(generated 45 tokens, read 35 tokens of prompt)
```

The exact wording and token counts will differ slightly between runs,
that's the model answering freely, same as any Gemini lesson. If the
command hangs for a long time instead, your machine may be
CPU-bound rather than GPU-accelerated, see Lesson 18 for what that
means for speed. If you see a connection error, check this course's
[README](../../README.md) and confirm `ollama --version` works.

## Checkpoint

- **`ollama.generate()`**: the simplest call, a raw prompt string in,
  a written answer out, blocking.
- **No API key**: local calls have nothing to authenticate, since
  there's no remote provider or quota.
- **`response.response`**: the written answer (an odd but correct
  attribute name).
- **`eval_count` / `prompt_eval_count`**: local token accounting,
  reported directly since there's no billing to hide it behind.

If anything here still feels unclear, ask before moving to Lesson 4.
