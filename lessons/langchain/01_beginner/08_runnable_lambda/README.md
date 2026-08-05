# Lesson 8: RunnableLambda, your own code inside a chain

## Where we left off

Every chain so far has been built entirely out of LangChain's own
pieces: templates, models, parsers. But real programs need custom logic
too, cleaning up messy user input, reformatting a result, computing
something extra. This lesson shows how to drop a plain Python function
into a chain, right alongside the built-in pieces.

## Two plain functions, nothing fancy

```python
def clean_question(raw_question: str) -> dict:
    cleaned = raw_question.strip()
    if not cleaned.endswith("?"):
        cleaned += "?"
    return {"question": cleaned}

def add_word_count(answer: str) -> dict:
    return {"answer": answer, "word_count": len(answer.split())}
```

Neither of these imports anything from LangChain. `clean_question` trims
whitespace and makes sure the text ends in a question mark. `add_word_count`
takes finished text and bundles it with how many words it has. Ordinary
Python, the kind you'd write with or without LangChain in the picture.

## Wrapping them with `RunnableLambda`

```python
clean_step = RunnableLambda(clean_question)
count_step = RunnableLambda(add_word_count)
```

`RunnableLambda` wraps a plain function so it gains the same interface
every other chain piece has, an `.invoke()` method, which is exactly what
lets it connect with `|` to a template, a model, or a parser. Without
this wrapper, `|` wouldn't know how to treat a bare function as a step.

## The full chain

```python
chain = clean_step | prompt | model | StrOutputParser() | count_step
```

Read this left to right, same as every chain since Lesson 6, just
longer: clean the raw input, and then fill in the template, and then
call the model, and then extract plain text, and then count its words.
Five steps, two of them are our own functions, three of them are
LangChain's, all connected the exact same way.

## Why `clean_question` returns a dict

```python
return {"question": cleaned}
```

The very next step in the chain is `prompt`, and `prompt` expects a
dictionary with a `"question"` key, exactly like every `.invoke({"question":
...})` call in earlier lessons. `clean_question`'s job isn't just "clean
the text", it's "produce whatever shape the next step in the chain
needs." This is the real discipline behind chaining anything with `|`:
each step's output has to match the next step's expected input, whether
that step is a LangChain built-in or your own function.

## Testing one step in isolation

```python
print(clean_step.invoke("  what is langchain  "))
# {'question': 'what is langchain?'}
```

Because `clean_step` has its own `.invoke()`, you can run it completely
on its own, no model call, no chain, just to check it does what you
expect. This is worth doing whenever you write a new step: verify it in
isolation before trusting it inside a longer chain.

## Running it

```bash
uv run python lessons/langchain/01_beginner/08_runnable_lambda/lesson.py
```

## Checkpoint

- **`RunnableLambda`**: wraps a plain Python function so it can be
  connected with `|` to any other chain step.
- **matching shapes**: each step's output must match the next step's
  expected input, whether it's a built-in or your own function.
- **testing in isolation**: any wrapped step can be `.invoke()`d on its
  own, separate from the full chain, to check it works correctly.

If anything here still feels unclear, ask before moving to Lesson 9.
