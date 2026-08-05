# Lesson 7: Output parsers, reshaping the reply automatically

## Where we left off

Since Lesson 1, every model response has been an `AIMessage` object, and
you've had to reach for `.text` yourself to get plain text out of it.
That's fine to do by hand once or twice, but tedious to repeat every
time. An **output parser** is a chain step that does that reshaping
automatically, as part of the pipeline itself.

## Without a parser: still an `AIMessage`

```python
plain_chain = prompt | model
plain_result = plain_chain.invoke({"question": "..."})
```

`plain_result` is an `AIMessage`, same as always. Nothing new here, this
is just Lesson 6's chain, no parser attached.

## `StrOutputParser`: automatic plain text

```python
str_chain = prompt | model | StrOutputParser()
str_result = str_chain.invoke({"question": "..."})
```

Adding `StrOutputParser()` as a third link means the chain now does one
more step after the model replies: reach into the `AIMessage` and pull
out just the text, the exact thing `.text` did manually. `str_result` is
already usable as plain text, no `.text` needed, `isinstance(str_result,
str)` is `True`.

(If you print its exact type, you might see something called
`TextAccessor` rather than `str`, that's an internal detail of how
LangChain represents text; it behaves like a normal string everywhere
that matters.)

## `JsonOutputParser`: automatic structured data

```python
json_chain = json_prompt | model | JsonOutputParser()
json_result = json_chain.invoke({"question": "..."})
```

This is a different kind of parser: instead of just extracting text, it
takes text that's *supposed to already be JSON* and turns it into a real
Python `dict`. That only works if the model actually replies with valid
JSON, which is why `json_prompt`'s system message explicitly demands
it:

```python
"Respond ONLY with JSON in the form "
'{{"answer": "...", "one_word_topic": "..."}}, nothing else.'
```

Notice the doubled curly braces, `{{` and `}}`. Templates already use
single `{}` for blanks like `{question}`, so a literal `{` or `}` you
actually want to appear in the text (here, real JSON syntax) has to be
escaped by doubling it. This is the same escaping convention Python's own
f-strings use.

Once parsed, `json_result` is a plain dictionary:

```python
json_result["one_word_topic"]  # e.g. "LangChain"
```

## The important distinction between these two parsers

`StrOutputParser` reshapes something the model *always* produces (text)
into a slightly more convenient form (plain text instead of a wrapped
object). `JsonOutputParser` is different: it *depends on the model
correctly following an instruction* (actually replying with valid JSON).
If the model ever slips and replies with something that isn't valid
JSON, `JsonOutputParser` will fail to parse it, an error, not silently
wrong data.

This is a real limitation you should know about now: free-text
instructions like "respond only with JSON" are a *request*, not a
*guarantee*. Lesson 18 introduces `with_structured_output`, a more
reliable way to get structured data that doesn't depend on the model
perfectly following a text instruction.

## Running it

```bash
uv run python lessons/langchain/01_beginner/07_output_parsers/lesson.py
```

## Checkpoint

- **output parser**: a chain step that reshapes the model's raw reply
  into something more directly usable.
- **`StrOutputParser`**: extracts plain text, same result as calling
  `.text` yourself, just automated.
- **`JsonOutputParser`**: parses text that's supposed to be JSON into a
  Python `dict`, but only works if the model actually produces valid
  JSON.
- **doubled `{{ }}`**: how you write a literal curly brace inside a
  template, since single `{}` means "blank to fill in."

If anything here still feels unclear, ask before moving to Lesson 8.
