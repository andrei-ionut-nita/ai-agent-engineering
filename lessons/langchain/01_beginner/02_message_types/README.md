# Lesson 2: Message types, System vs Human vs AI

## Where we left off

Lesson 1 sent a single bare string:

```python
model.invoke("In one sentence, what is LangChain for?")
```

That works, but it's limited. There's no way to say "behave a certain
way" separately from "here's my actual question", they're smushed
together into one plain string. This lesson introduces a better format:
a **list of labeled messages**.

## Three message types

```python
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
```

- **`SystemMessage`**: standing instructions, how the AI should behave.
  Not something the user said, it's configuration for the whole
  conversation.
- **`HumanMessage`**: something the user (you) said.
- **`AIMessage`**: something the AI said back. You saw this already,
  Lesson 1's `response` was secretly an `AIMessage` the whole time, we
  just never looked at its type directly.

## Sending a list instead of a string

```python
messages = [
    SystemMessage("You are a pirate. Answer everything in pirate speak."),
    HumanMessage("What is LangChain?"),
]
response = model.invoke(messages)
```

`.invoke()` accepts either a bare string (Lesson 1's way) or a list of
messages (this lesson's way). A bare string is actually shorthand,
LangChain quietly turns it into a single `HumanMessage` behind the
scenes. Writing the list explicitly is what gives you the ability to add
a `SystemMessage` alongside it, something a bare string can't do on its
own.

Run this and the reply comes back in full pirate speak, proof the
`SystemMessage` actually shaped the AI's behavior, separately from the
question itself.

## A first look at what "memory" will mean

```python
messages.append(response)
messages.append(HumanMessage("Say that again, but in one word."))
second_response = model.invoke(messages)
```

Here's something worth noticing closely. We took the AI's own reply
(`response`, an `AIMessage`) and added it back into our list, then added
a new question, then sent the **whole list** again, not just the new
question.

The result: the model correctly answers "Arrr!", a one-word pirate
summary of what it just said. It only knows what "that" refers to
because we resent its own earlier reply back to it, alongside the new
question. Nothing was actually remembered by the model itself, this
list is the only place that earlier exchange lives, and we chose to
include it. Lesson 17 will make this exact mechanism the whole point,
but seeing it happen here, early, matters, it demystifies "memory"
before it ever gets called by that name.

## Running it

```bash
uv run python lessons/langchain/01_beginner/02_message_types/lesson.py
```

## Checkpoint

- **`SystemMessage`**: standing instructions, separate from what the
  user actually said.
- **`HumanMessage`**: what the user said. A bare string passed to
  `.invoke()` is automatically treated as one of these.
- **`AIMessage`**: what the AI said back. Every response you've received
  since Lesson 1 has secretly been one of these.
- **sending a list**: `.invoke()` reads the whole list as one
  conversation, in order, top to bottom.

If anything here still feels unclear, ask before moving to Lesson 3.
