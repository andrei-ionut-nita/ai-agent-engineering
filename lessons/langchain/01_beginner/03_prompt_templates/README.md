# Lesson 3: Prompt templates, filling in blanks

## The problem with Lessons 1 and 2

So far, every message we sent was written directly into the code:

```python
model.invoke("In one sentence, what is LangChain for?")
```

That's fine once. But real programs need to:

- Give the AI standing instructions (a personality, a rule like "keep
  answers short") without retyping those instructions into every message.
- Send many different questions that share the same instructions, where
  only a small part of the message actually changes each time.

A **prompt template** solves both.

## A template is a message with a blank

```python
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a concise research assistant. Answer in at most two sentences."),
        ("human", "{question}"),
    ]
)
```

If you've used Python f-strings (`f"Hello {name}"`), this is the same
idea: `{question}` is a placeholder, not a real question yet, it gets
filled in later.

Two kinds of entries here:

- **`"system"`**: standing instructions for how the AI should behave.
  Fixed, never changes between requests.
- **`"human"`**: the user's actual message. Here it's a placeholder,
  waiting to be filled in.

Building this template is a one-time cost. From then on, "be a concise
research assistant" applies automatically to every question you run
through it, without repeating the instruction.

## Filling in the blank

```python
filled_prompt = prompt.invoke({"question": "What is LangChain for?"})
```

`{"question": "..."}` is a dictionary: a label (`"question"`) paired
with a value. LangChain matches that label against the `{question}`
placeholder in the template and pours the value in. The label and the
placeholder name **must match exactly**. Typo it (`"query"` instead of
`"question"`) and LangChain raises an error, it has no way to know what
fills the blank.

`filled_prompt` isn't text yet, it's a small object holding the finished
list of messages. Calling `.to_messages()` on it shows you exactly what
will be sent:

```
[system] You are a concise research assistant. Answer in at most two sentences.
[human] What is LangChain for?
```

## Sending it to the model

```python
response = model.invoke(filled_prompt)
```

Same `.invoke()` from every earlier lesson. The only difference: instead
of a single string, we're handing it a filled-in template, a full list of
messages (system + human).

## Why two separate steps, instead of one?

You'll notice this lesson calls `prompt.invoke()` and then
`model.invoke()` as two distinct lines, rather than connecting them with
`|` like you might have seen in tutorials. That's deliberate: Lesson 6
introduces `|` as its own concept. Here, the goal is just to understand
what a template does, on its own, before adding anything else on top of
it.

## Running it

```bash
uv run python lessons/langchain/01_beginner/03_prompt_templates/lesson.py
```

## Try this yourself

Change `"What is LangChain for?"` to a different question, rerun it, and
notice the printed "Filled-in messages" section shows your new question
slotted into the same unchanged system instructions.

## Checkpoint

- **prompt template**: a message structure with placeholders, filled in
  at call time.
- **system message**: standing instructions, applied to every message
  sent through this template.
- **`{placeholder}`**: matched against dictionary keys by exact name.
- **`.invoke()` on a template**: fills in the blanks, returns a ready
  list of messages, doesn't call the AI yet.

If anything here still feels unclear, ask before moving to Lesson 4.
