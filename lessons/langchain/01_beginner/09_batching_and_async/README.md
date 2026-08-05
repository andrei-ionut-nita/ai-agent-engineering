# Lesson 9: Batching and async, running more than one call at once

## The problem with a loop of `.invoke()` calls

Every call to `.invoke()` since Lesson 1 has been one question, one
answer, one round trip over the network. If you need answers to three
different questions, the obvious approach is a loop:

```python
for thing in things:
    chain.invoke({"thing": thing})
```

This works, but it's slow in a specific way: each `.invoke()` waits for
its network round trip to fully finish before the next one even starts.
Three questions means three round trips, back to back, with no overlap.

## `.batch()`: many inputs, run concurrently

```python
chain.batch([{"thing": thing} for thing in things])
```

`.batch()` takes a list of inputs and lets LangChain start all of their
network requests at (roughly) the same time, instead of one after
another. The requests overlap while they're waiting on the network,
rather than queuing up. Run this lesson and compare the two printed
times, `chain.batch()` finishing in roughly half the time (or less) of
the sequential loop for the same three questions is the concurrency
actually paying off.

## `.ainvoke()` and `asyncio`: the same idea, written explicitly

```python
await asyncio.gather(*(chain.ainvoke({"thing": thing}) for thing in things))
```

`.ainvoke()` is the **async** version of `.invoke()`. If you haven't
used Python's `async`/`await` before: it's a way of saying "start this,
but don't block everything else while waiting for it to finish."
`asyncio.gather(...)` starts several async calls at once and waits for
all of them together, similar in spirit to what `.batch()` does, but
written with Python's own async tools instead of a LangChain-provided
shortcut.

In practice, `.batch()` is simpler to reach for; `.ainvoke()` matters
more once your own program is already async (for example, a web server
handling many users at once).

## Why three DIFFERENT sets of questions?

Look closely at the code: sequential, batched, and async each use a
*different* set of three things (sky/grass/banana vs. fire truck/snow/
eggplant vs. school bus/coal/flamingo), not the same three questions
three times. This is deliberate.

Google's Gemini API automatically caches recently-seen identical
prompts, if all three phases asked about "the sky," the second and
third phases might come back suspiciously fast for a reason that has
nothing to do with batching or async, just because the answer was
already cached from the first phase. Using distinct questions for each
phase keeps the comparison honest: any speed difference you see is
really about concurrency, not caching.

## Running it

```bash
uv run python lessons/langchain/01_beginner/09_batching_and_async/lesson.py
```

You should see something like:

```
Sequential .invoke() x3: 1.17s
chain.batch() x3:        0.51s
asyncio.gather + ainvoke: 0.44s
```

Exact numbers will vary run to run, network conditions aren't constant,
but batched/async should consistently beat sequential for the same
number of questions.

## Checkpoint

- **sequential `.invoke()` in a loop**: correct, but each call waits for
  the previous one to fully finish, no overlap.
- **`.batch()`**: runs a list of inputs concurrently, overlapping their
  network wait time instead of queuing them.
- **`.ainvoke()` + `asyncio.gather`**: the same concurrency idea, written
  with Python's own async/await instead of a LangChain shortcut.
- **why distinct test questions matter**: avoids an unrelated feature
  (prompt caching) accidentally making one phase look faster than it
  really is for the reason you think.

If anything here still feels unclear, ask before moving to Lesson 10.
