# Lesson 6: Model parameters

## `options`, one dict for everything

Every call so far has used a model's defaults. `ollama.chat()` and
`ollama.generate()` both accept an `options` dict that tunes *how* the
model generates, separate from *what* you ask it. This lesson covers
the three you'll reach for most: `temperature`, `seed`, and
`num_predict`.

## `temperature`: randomness

At each step, a model doesn't pick one "correct" next word, it
computes a probability for every word in its vocabulary and samples
from that distribution. `temperature` controls how sharply that
sampling favors the most likely option:

- **`temperature=0.0`**: always take the single most probable next
  word. Deterministic (same input, same output) and reliable, but
  repetitive, the model can't surprise you or vary its phrasing.
- **Higher values** (`1.0` is a common default, this lesson goes to
  `1.5`): let less-likely words get picked sometimes, producing more
  varied, more "creative" output, at the cost of losing that
  repeatability and, past a point, coherence.

There's no universally right value, low temperature for factual
lookups and structured extraction (Lesson 10), higher for brainstorming
or creative writing.

## `seed`: reproducibility

Even at `temperature=0.0`, some randomness can creep in from how the
model's internals are computed. `seed` pins the random number
generator itself to a fixed starting point, so the same prompt with
the same `temperature` and `seed` produces the identical answer every
time, useful for tests and debugging, where "did my prompt change
actually change the output" needs a real answer.

## `num_predict`: a hard length cap

`temperature` shapes *what* the model says; `num_predict` limits *how
much*. It's a hard ceiling on the number of tokens generated,
regardless of whether the model was in the middle of a sentence. Set
it low enough and you'll see the answer cut off mid-thought, which is
exactly what the third example below demonstrates on purpose.

## Running it

```bash
uv run python lessons/ollama/01_beginner/06_model_parameters/lesson.py
```

## Expected output

```
temperature=0.0, seed=42, asked twice:
  Apple.
  Apple.

temperature=1.5, a creative prompt:
  "Brewing Joy, One Cup"

num_predict=5, an open-ended prompt:
  The water cycle, also
```

The first two lines should be identical to each other every time you
run this (that's `temperature=0.0` plus a fixed `seed` doing its job).
The tagline and the cut-off explanation will vary between runs, and
the cut-off point may land on a slightly different word depending on
tokenization, the point is that it stops abruptly mid-sentence.

## Checkpoint

- **`options`**: the dict argument to `chat()`/`generate()` that tunes
  generation behavior, separate from the prompt itself.
- **`temperature`**: randomness, `0.0` is deterministic and repetitive,
  higher is varied and less predictable.
- **`seed`**: pins randomness to a fixed starting point, for exact
  reproducibility.
- **`num_predict`**: a hard cap on generated tokens, cuts off mid-answer
  if reached.

If anything here still feels unclear, ask before moving to Lesson 7.
