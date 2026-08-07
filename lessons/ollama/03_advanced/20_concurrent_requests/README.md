# Lesson 20: Concurrent Requests

## One server, several requests

Every lesson so far has sent one request, waited for the reply, then
moved on. A real application, especially one serving more than one
user, often needs to handle several requests to the same local Ollama
server at once. This lesson compares sending requests one at a time
against sending them concurrently, from several threads.

## Why threads, not `asyncio`, for this

`ollama.chat()` is a blocking call: your program pauses on the network
round trip to `localhost:11434` until a reply comes back. That's
exactly the situation Python threads handle well, even with the
Global Interpreter Lock, a thread that's blocked waiting on network
I/O isn't holding up other threads from making progress. (The `ollama`
package also ships an `AsyncClient` for `asyncio`-based code, if your
program is already structured that way; threads are used here because
they need no other changes to code you've already written in this
course.)

## The code, piece by piece

```python
for i in range(n):
    ask(i)
sequential_total = time.time() - start
```

Baseline: each call fully completes before the next one starts. Total
time is roughly the sum of every individual call's time.

```python
with concurrent.futures.ThreadPoolExecutor(max_workers=n) as executor:
    results = list(executor.map(ask, range(n)))
```

`ThreadPoolExecutor` runs `ask()` for all `n` values at once, each in
its own thread, all hitting the same local Ollama server
simultaneously. `executor.map()` blocks until every call finishes and
returns results in the original order, regardless of which thread
happened to finish first.

## What Ollama does with multiple requests at once

Ollama can serve multiple requests concurrently, up to a limit
controlled by the `OLLAMA_NUM_PARALLEL` environment variable
(server-side, not something this lesson's code sets), and bounded by
how much VRAM/RAM is available to hold the model's active state for
each simultaneous request. Requests beyond that limit queue and wait
their turn rather than failing outright. This is why concurrent
requests here don't take four times as long as one request. They
genuinely overlap. But it's also not free: pushing far more concurrent
load than your hardware and `OLLAMA_NUM_PARALLEL` can actually support
will eventually just shift the wait from your code to Ollama's queue.

## Running it

```bash
uv run python lessons/ollama/03_advanced/20_concurrent_requests/lesson.py
```

## Expected output

Exact timings depend heavily on your hardware, but concurrent should
be noticeably faster than sequential:

```
Sequential: 4 calls in 0.40s total
Concurrent: 4 calls in 0.19s total
  request 0: 0.14s, answered '0'
  request 1: 0.19s, answered '1'
  request 2: 0.16s, answered '2'
  request 3: 0.12s, answered '3'
```

Each individual concurrent request may take slightly longer than a
lone sequential request would (they're sharing the server), but the
*total* time for all four should still be well under the sequential
total.

## Checkpoint

- **`ollama.chat()` is blocking**: threads can genuinely overlap that
  waiting time, even under Python's GIL.
- **`ThreadPoolExecutor.map()`**: runs several calls concurrently,
  returns results in the original order.
- **`OLLAMA_NUM_PARALLEL`**: server-side limit on how many requests
  Ollama actually processes at once, beyond it, requests queue.
- **The tradeoff**: concurrency helps up to your hardware's real
  capacity, past that, load just shifts into a queue instead of
  disappearing.

If anything here still feels unclear, ask before moving to Lesson 21.
