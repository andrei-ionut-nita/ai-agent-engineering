# Lesson 33: Async and concurrency

## Every call so far has blocked

Since Lesson 1, `.invoke()` has meant "send this, and freeze the entire
program until the answer comes back." For one call at a time, that's
fine. For several independent calls, it's wasteful: each one spends most
of its time just waiting on the network, and there's no reason those
waits can't overlap. `.ainvoke()` is the async twin of `.invoke()`, and
`asyncio.gather` is what lets several of them wait at the same time
instead of one after another.

## Nodes don't need to change

```python
def chatbot(state: MessagesState) -> dict:
    response = model.invoke(state["messages"])
    return {"messages": [response]}
```

This node is written exactly like every other node in the course, a
plain, synchronous function. LangGraph handles the async plumbing from
the outside, calling it via `.ainvoke()`/`.astream()` doesn't require
rewriting node functions as `async def` themselves.

## The async call itself

```python
async def ask_async(question: str) -> str:
    result = await app.ainvoke({"messages": [HumanMessage(question)]})
    return result["messages"][-1].text
```

Same shape as `.invoke()`, same result structure, the only difference is
`await` in front of it. Inside an `async def` function, `await` pauses
*this* coroutine without blocking the rest of the program, other
coroutines can keep running during that wait.

## Sequential vs. concurrent, measured

```python
async def run_sequential() -> float:
    start = time.perf_counter()
    for question in QUESTIONS:
        await ask_async(question)
    return time.perf_counter() - start

async def run_concurrent() -> float:
    start = time.perf_counter()
    await asyncio.gather(*(ask_async(question) for question in QUESTIONS))
    return time.perf_counter() - start
```

`run_sequential` awaits each call before starting the next, so total time
is roughly the sum of all three. `run_concurrent` starts all three
`ask_async` coroutines essentially at once via `asyncio.gather`, so total
time is closer to the *slowest single call*, not the sum of all of them.

## Running it

```bash
uv run python lessons/langgraph/03_advanced/33_async_and_concurrency/lesson.py
```

You'll see two wall-clock timings printed, sequential and concurrent, for
the same three questions, followed by the actual speedup measured on
this run (typically 2 to 3x for three concurrent calls).

## Checkpoint

- **`.ainvoke()` / `.astream()`**: async counterparts of `.invoke()` /
  `.stream()`, same result shapes, non-blocking while waiting.
- **`asyncio.gather(...)`**: runs several coroutines concurrently,
  waiting on all of them together instead of one at a time.
- **nodes stay synchronous**: you don't need `async def` node functions
  to benefit from `.ainvoke()` at the graph level.
- **why concurrency helps here specifically**: each call spends most of
  its time waiting on the network, exactly the kind of wait that
  overlaps well with other waits.

If anything here still feels unclear, ask before moving to Lesson 34.
