# Lesson 10: Model parameters, and an honest surprise

## What we're trying to control

Every model call so far has used whatever defaults `ChatGoogleGenerativeAI`
picked for us. Two parameters are worth knowing how to control directly:

- **`temperature`**: how willing the model is to pick a less-likely next
  word instead of the most-likely one. Low (near 0) tends to produce the
  same or very similar answer every time you ask; high (near 1 or above)
  tends to produce more varied answers to the exact same question.
- **`max_output_tokens`**: a hard cap on how long the reply is allowed to
  be. A **token** is roughly a word-piece, not exactly a word or a
  character, models don't count length in letters, they count it in
  tokens.

```python
steady_model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0)
creative_model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=1.0)
```

## An honest surprise

Run this lesson and you'll likely see a warning like:

```
UserWarning: Model 'gemini-3.5-flash-lite' uses fixed sampling defaults;
the sampling parameter(s) temperature will be ignored.
```

And sure enough, comparing the `temperature=0` answers to the
`temperature=1.0` answers, both lists look similarly varied, `temperature`
had no visible effect. This isn't a bug in the lesson, it's a real,
useful fact: **`gemini-3.5-flash-lite` is a small, fast, distilled model,
and Google has fixed its sampling settings internally**, this specific
parameter simply doesn't apply to it, no matter what value you pass.

This is worth sitting with, because it generalizes: not every model
supports every parameter, and the shared LangChain interface (the same
`ChatGoogleGenerativeAI` class, the same `temperature=` keyword) doesn't
guarantee every underlying model actually honors every setting. When
something you configure doesn't seem to change anything, checking for a
warning like this one, or the provider's own documentation for that
specific model, is the right instinct, not assuming your code is wrong.

If you want to see `temperature` actually working, the same code would
behave differently on a bigger model in the same family (like
`gemini-3.5-flash`, without `-lite`) that doesn't fix its sampling
settings, at the cost of a much lower free daily request limit, which is
exactly why this project defaults to the `-lite` model everywhere else.

## `max_output_tokens`: this one does work

```python
short_model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", max_output_tokens=10)
long_answer = short_model.invoke("Explain what LangChain is.")
```

Unlike `temperature`, `max_output_tokens` is respected. Asking a
naturally long question ("Explain what LangChain is.") with a tiny
10-token cap produces a reply that's visibly cut off mid-thought,
something like `"**LangChain** is an"`, and then nothing more. The model
wasn't finished, it simply ran out of allowed length.

## Running it

```bash
uv run python lessons/langchain/01_beginner/10_model_parameters/lesson.py
```

## Checkpoint

- **`temperature`**: controls randomness in word choice, in theory, but
  not every model actually honors it.
- **`max_output_tokens`**: a hard cap on reply length, measured in
  tokens (word-pieces), not characters or words.
- **not every parameter works on every model**: the shared LangChain
  interface doesn't guarantee every setting is honored underneath, watch
  for warnings, and check provider docs when something seems to have no
  effect.

If anything here still feels unclear, ask before moving to Lesson 11.
