# Lesson 5: Streaming a reply

## The problem with waiting

Every call so far has been blocking: your program pauses on
`ollama.chat()` until the model has finished writing its *entire*
answer, then everything appears on screen at once. For a short answer
that's fine; for a long one, a real user is left staring at nothing
for however many seconds generation takes, even though the model
already has the first sentence ready long before the last one.

Streaming fixes that by handing you each piece of the answer as soon
as it exists, instead of making you wait for all of it.

## The code, piece by piece

```python
stream = ollama.chat(
    model="llama3.2",
    messages=[...],
    stream=True,
)
```

The single new argument, `stream=True`, changes what `ollama.chat()`
returns: instead of one complete `ChatResponse`, you get an iterator
you can loop over, one that yields a new small `ChatResponse` "chunk"
every time the model has generated a bit more text.

```python
for chunk in stream:
    print(chunk.message.content, end="", flush=True)
```

Each `chunk` has the same shape as the single response from Lesson 4,
just with `.message.content` holding a fragment (often a word or two)
instead of the whole answer. `end=""` stops `print` from adding its
own newline after every fragment, and `flush=True` forces Python to
show it on screen immediately rather than buffering it, both needed
to get a genuinely live, word-by-word typing effect in the terminal.

```python
if chunk.done:
    break
```

The stream's last chunk has `done=True` and empty content, it's a
signal that generation has finished, not more text to print. Looping
over the iterator until it naturally ends works too; checking `.done`
explicitly here just makes that final signal visible in the code.

This is the same idea as `.stream()` on a LangChain model in the
langchain course, applied to a local model instead of Gemini.

## Running it

```bash
uv run python lessons/ollama/01_beginner/05_streaming_responses/lesson.py
```

Watch the terminal while it runs, the numbers should appear one at a
time rather than all at once, that live effect is the entire point of
this lesson and won't come through in a static transcript.

## Expected output

```
1

2

3

4

5

(received 10 chunks)
```

The chunk count can vary slightly run to run (models don't always
split text into fragments the same way twice), but you should see it
land somewhere around 8-12 for this short a reply, each digit and
newline arriving as its own piece.

## Checkpoint

- **`stream=True`**: turns `ollama.chat()`'s return value into an
  iterator of small chunks instead of one complete response.
- **Each chunk**: same shape as a full response, `.message.content`
  holds a fragment of text, `.done` marks the final, contentless chunk.
- **`end=""`, `flush=True`**: what makes `print()` show fragments
  immediately instead of buffering a full line.
- **Why it matters**: a user sees the answer forming in real time
  instead of staring at nothing until generation fully finishes.

If anything here still feels unclear, ask before moving to Lesson 6.
