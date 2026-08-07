# Lesson 15: Comparing Models

## Before this lesson

Pull all three models used here, if you haven't already:

```bash
ollama pull llama3.2:1b
ollama pull llama3.2
ollama pull llama3
```

That's roughly 1.3 GB, 2 GB, and 4.7 GB respectively, about 8 GB of
disk in total.

## Size isn't the only axis, but it's the biggest one

Lesson 2 showed how tags pick a specific size within a model family.
This lesson compares three real points on that spectrum directly:
`llama3.2:1b` (1.2B parameters), `llama3.2` (3.2B), and `llama3` (8B),
on the same prompt, timed.

The pattern holds in general, though exact numbers depend entirely on
your hardware: smaller models generate faster (more tokens per second)
but tend to write shorter, sometimes less nuanced answers; larger
models are slower but generally more capable. Neither extreme is
"correct", it's a real tradeoff you make per use case: a background
classification task might be happy with `1b`, a careful multi-step
agent probably wants more capability, even at the cost of speed.

## The load-time trap

```python
print("Warming up (loading each model into memory once)...")
for model in MODELS:
    ollama.chat(model=model, messages=[{"role": "user", "content": "hi"}])
```

Only one model actively generates on your hardware at a time. If you
naively time three different models back to back without this warm-up
step, your numbers get badly skewed: whichever model *wasn't* already
loaded pays a one-time cost to swap into memory, on top of its actual
generation time, and that swap cost has nothing to do with the
model's real speed. This lesson calls every model once first,
specifically so the timed comparison that follows measures generation
speed alone, not loading. Skip this step in your own benchmarking and
you'll draw the wrong conclusions about which model is "faster."

## The code, piece by piece

```python
def timed_chat(model: str) -> tuple[float, int]:
    start = time.time()
    response = ollama.chat(..., options={"temperature": 0.7, "seed": 7})
    elapsed = time.time() - start
    return elapsed, response.eval_count
```

Nothing new mechanically, `time.time()` around a call you've already
made a dozen times in this course, paired with `response.eval_count`
from Lesson 3 to compute a genuinely comparable tokens-per-second rate,
since raw elapsed time alone isn't fair when models don't generate the
same number of tokens for the same prompt.

## Running it

```bash
uv run python lessons/ollama/02_intermediate/15_comparing_models/lesson.py
```

## Expected output

Exact numbers depend entirely on your CPU/GPU, but the shape and
relative ordering (smaller models faster) should hold:

```
Warming up (loading each model into memory once)...

Timed generation, same prompt, all models already warm:

  llama3.2:1b: 0.19s, 17 tokens, 90.6 tok/s
  llama3.2: 0.24s, 17 tokens, 72.1 tok/s
  llama3: 0.56s, 26 tokens, 46.5 tok/s
```

## Checkpoint

- **Size vs speed vs quality**: smaller models generate faster but are
  generally less capable, no single "best" choice, it depends on the task.
- **The load-time trap**: swapping to a different model has a one-time
  loading cost, warm up before benchmarking or your numbers lie.
- **Tokens per second**: a fairer comparison metric than raw elapsed
  time, since different models write different-length answers.

If anything here still feels unclear, ask before moving to Lesson 16.
