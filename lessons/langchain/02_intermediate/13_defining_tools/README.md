# Lesson 13: Defining a tool

## Why tools exist

A language model is really good at writing sentences, but it's actually
bad at exact math. Ask it to multiply two big numbers and it will often
guess something that *looks* plausible but is wrong, because it isn't
calculating, it's predicting what word or digit is statistically likely
to come next, based on patterns it saw during training.

So instead of trusting the model to do math itself, later lessons will
give it access to a **tool**: a real Python function that does exact
math. This lesson is entirely about the tool itself, no AI involved yet,
so the next lesson can focus purely on how an AI decides to use one.

## The tool: a calculator

```python
@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression, e.g. '12 * (7 + 3)'."""
    tree = ast.parse(expression, mode="eval")
    return str(_eval(tree.body))
```

`@tool` is a **decorator**, a way of wrapping a normal function with
extra behavior without changing what it looks like from the outside.
`@tool` wraps `calculator` so LangChain can describe it to an AI later:
its name (`calculator`), what it does (the docstring, the text in triple
quotes right under the function), and what input it expects
(`expression`, a string).

## Why not just use Python's `eval()`?

Python has a built-in `eval()` that runs any string as code. It would
make this a one-line tool. But an AI will eventually be the one deciding
what string to pass in here, and trusting an AI-generated string to run
as raw code is dangerous: if it ever produced something like
`"os.system('delete everything')"`, plain `eval()` would actually run it.

`_eval` sidesteps this entirely. `ast.parse(expression, mode="eval")`
reuses Python's own parser to turn the string into a tree, without
running anything yet. Our `_eval` function then walks that tree, but only
knows how to perform addition, subtraction, multiplication, division, and
powers, nothing else. There's nothing harmful it's capable of doing, no
matter how strange the input, because those five operations are all it
understands.

This is a real security principle worth remembering: **never run
untrusted text as code**, restrict it to only what you intend to allow.

## Calling the tool directly

```python
result = calculator.invoke({"expression": "12 * (7 + 3)"})
```

Even though no AI is involved yet, `calculator` isn't a plain function
anymore, `@tool` turned it into a small object with its own `.invoke()`
method, same method name you've used on models and chains since Lesson
1. That consistency isn't an accident, in LangChain, tools, models, and
chains all implement the same basic interface.

## Inspecting what the AI will see

```python
print(calculator.name)          # "calculator"
print(calculator.description)   # the docstring
print(calculator.args)          # {'expression': {'title': 'Expression', 'type': 'string'}}
```

This is worth sitting with: **the AI will never see the actual
implementation**, not `_eval`, not `ast`, none of it. It only ever sees
these three things: a name, a description, and an argument schema.

Everything the AI knows about this tool comes from what you print here.
If the docstring is vague, the AI will misuse the tool; if it's
precise, the AI will use it correctly. Writing a good docstring is not
just documentation for humans, in this case it's the entire instruction
manual an AI has to work with.

## Running it

```bash
uv run python lessons/langchain/02_intermediate/13_defining_tools/lesson.py
```

## Checkpoint

- **tool**: a real Python function, wrapped so it can be described to,
  and eventually called by, an AI.
- **`@tool` decorator**: wraps a function, attaching a name, description,
  and argument schema pulled from its signature and docstring.
- **why not `eval()`**: never run untrusted (especially AI-generated)
  text as code; restrict to a fixed, safe set of operations instead.
- **what the AI sees**: only the name, description, and argument schema,
  never your actual implementation.

If anything here still feels unclear, ask before moving to Lesson 14,
where we actually hand this tool to a model.
