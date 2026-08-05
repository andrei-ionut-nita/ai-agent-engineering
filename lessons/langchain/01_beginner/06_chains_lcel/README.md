# Lesson 6: Chains, connecting steps with `|`

## Where we left off

In Lesson 3, filling in a template and calling the model were two
separate, visible lines:

```python
filled_prompt = prompt.invoke({"question": "..."})
response = model.invoke(filled_prompt)
```

That's clear, but a little clunky if you're going to do it the same way,
over and over, for many different questions. A **chain** connects these
steps into one reusable pipeline.

## The `|` operator

```python
chain = prompt | model
```

Read `|` as "and then." This line means: *fill in the prompt template,
and then send it to the model.* Once built, `chain` behaves like a single
unit, you can call `.invoke()` on it directly:

```python
response = chain.invoke({"question": "What is LangChain for?"})
```

Under the hood, this does exactly what Lesson 3 did by hand: `prompt`
fills the blank, its output feeds directly into `model`, and `model`'s
reply comes back out. The difference is you built the wiring once, as
`chain`, and can now reuse it as many times as you like without
rewriting those two lines each time, as shown in `main()` calling
`chain.invoke(...)` twice with two different questions.

## Why is this called "LCEL"?

LangChain calls this style of composing steps with `|` **LCEL**
("LangChain Expression Language"). It's not a separate programming
language, it's just this operator-based way of wiring `Runnable` objects
(anything with an `.invoke()` method, like `prompt` and `model`) together.
Almost everything in LangChain implements this same interface, which is
why `|` works between so many different kinds of objects.

## What this buys you, beyond saving two lines

Because `chain` is one object now, it inherits some abilities you didn't
have to build yourself:

- `chain.batch([...])` can run many different inputs at once (Lesson 9
  covers this properly).
- `chain.stream(...)` can show the answer arriving piece by piece instead
  of waiting for the whole thing (Lesson 19 covers this properly).

You don't need to understand those yet, just know they exist *because*
`chain` is a single composed unit, not two separate calls. This is the
actual payoff of chains: build the pipeline once, and every future
capability layered on top applies to the whole thing at once.

## Running it

```bash
uv run python lessons/langchain/01_beginner/06_chains_lcel/lesson.py
```

You should see two different answers printed, both produced by the same
`chain`, reused for two separate questions.

## Checkpoint

- **chain**: multiple steps (here: a template and a model) connected with
  `|`, so they behave as a single reusable pipeline.
- **`|`**: reads as "and then", feeds one step's output into the next
  step's input.
- **LCEL**: LangChain's name for this style of composing `Runnable`
  objects with `|`.

If anything here still feels unclear, ask before moving to Lesson 7.
