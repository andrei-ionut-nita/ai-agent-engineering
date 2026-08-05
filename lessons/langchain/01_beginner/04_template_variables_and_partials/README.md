# Lesson 4: Multiple blanks, and pre-filling some with `.partial()`

## Where we left off

Lesson 3's template had exactly one blank, `{question}`. Real templates
often need more than one. This lesson adds a second blank, `{persona}`,
and introduces a shortcut for when one blank is fixed for a while but
another keeps changing.

## Two blanks in one template

```python
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are {persona}. Answer in at most two sentences."),
        ("human", "{question}"),
    ]
)
```

Nothing conceptually new here beyond Lesson 3, just two placeholders
instead of one. Filling them in works the same way, a dictionary with a
key matching each blank's name:

```python
filled = prompt.invoke({"persona": "a pirate", "question": "What is LangChain?"})
```

Both `persona` and `question` must be present in the dictionary, or
LangChain won't have a value for one of the blanks and will raise an
error, same rule as Lesson 3, just now applying to two keys instead of
one.

## The problem `.partial()` solves

Imagine `persona` is decided once, at the start of a session (say, the
user picked "a pirate" from a menu), but `question` is going to be
different every single time the user asks something. Passing
`{"persona": "a pirate", "question": ...}` on every single call means
repeating `persona` every time, even though it never actually changes.

```python
pirate_prompt = prompt.partial(persona="a pirate")
```

`.partial()` locks in a value for one (or more) of the blanks ahead of
time, and hands back a *new* template that only still has the remaining
blank(s) open. `pirate_prompt` now only needs `{"question": ...}`,
`persona` is already baked in.

```python
filled_again = pirate_prompt.invoke({"question": "What is a prompt template?"})
```

Notice this call only passes one key. Run the lesson and you'll see the
pirate persona still shapes the answer, even though we never mentioned
"pirate" again after building `pirate_prompt`.

## Why this matters beyond saving a few keystrokes

This is the same shape of problem you'll see again in later lessons:
some configuration is fixed for a whole session (a persona, a system
role, a user's name), while other input changes on every call (the
actual question). `.partial()` is how LangChain lets you separate those
two categories cleanly: decide the fixed part once, and only worry about
the changing part from then on.

## Running it

```bash
uv run python lessons/langchain/01_beginner/04_template_variables_and_partials/lesson.py
```

## Checkpoint

- **multiple blanks**: a template can have as many `{placeholder}`s as
  you need, each filled by a matching dictionary key.
- **`.partial()`**: pre-fills one or more blanks ahead of time, returning
  a new template that only still needs the remaining ones.
- **why it matters**: separates configuration that's fixed for a session
  from input that changes on every call.

If anything here still feels unclear, ask before moving to Lesson 5.
