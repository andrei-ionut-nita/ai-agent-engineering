# Lesson 19: Streaming, showing the answer as it's produced

## The problem `.invoke()` always had

Every single `.invoke()` call since Lesson 1 works the same way: you
call it, your program pauses completely, and it stays paused until the
model has finished generating its *entire* reply, however long that
takes. Only then does anything come back to you at all.

## `.stream()`: an iterator of chunks, not one final answer

```python
for chunk in chain.stream({}):
    print(chunk.text, end="", flush=True)
```

`.stream()` doesn't hand back one `AIMessage`. It hands back something
you loop over, an iterator, that produces small **chunks** of the reply
as they become available, while the model is still generating the rest.
Each `chunk` behaves like a small `AIMessage` in its own right, with its
own `.text`, you're meant to print (or otherwise use) each piece as it
arrives, rather than waiting to collect the whole thing first.

`end=""` in the `print()` call matters here: by default, `print()` adds
a newline after every call, which would put each chunk on its own line.
`end=""` suppresses that, so the chunks run together into one flowing
line of text, the effect you've probably seen in ChatGPT or similar
apps, words appearing progressively rather than all at once.

## What running this lesson actually showed

This lesson timed both approaches. On this run, `.invoke()` didn't print
anything for **about 47 seconds**, then the entire three-sentence story
appeared all at once. `.stream()`, asked for the exact same kind of
story, printed its *first* chunk in **under two seconds**, then kept
printing more chunks as they arrived, finishing the whole story well
before `.invoke()` would have shown anything at all.

This is a genuinely large gap, larger than you might expect, and it's
real: whatever the model is doing to fully finish a reply can take much
longer than the time it takes for the *first piece* of that reply to be
ready. `.invoke()` makes you wait for all of it. `.stream()` shows you
the beginning as soon as it exists.

## Why this matters beyond feeling snappier

This isn't just a cosmetic improvement. Waiting 47 seconds staring at
nothing feels broken, even though the program is working correctly the
whole time. Streaming doesn't make the model faster, the total time to
finish the full reply is roughly the same either way, but it changes
*when* the user sees the first sign of progress, from "after everything
is done" to "almost immediately." For anything longer than a very short
reply, that difference is the difference between an app that feels
responsive and one that feels frozen.

## Running it

```bash
uv run python lessons/langchain/02_intermediate/19_streaming/lesson.py
```

Expect a long pause before the `.invoke()` section prints anything,
that's normal and is the entire point, followed by the `.stream()`
section visibly typing itself out, much sooner and much faster-feeling.

## Checkpoint

- **`.invoke()`**: waits for the model's entire reply before returning
  anything at all, however long that takes.
- **`.stream()`**: returns chunks progressively, as they're generated,
  instead of waiting for the full reply.
- **why it matters**: same total generation time either way, but a
  dramatically different, much faster feeling first response.

If anything here still feels unclear, ask before moving to Lesson 20.
