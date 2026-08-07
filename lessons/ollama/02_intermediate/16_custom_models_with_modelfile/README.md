# Lesson 16: Custom Models With a Modelfile

## Baking in what you'd otherwise repeat every call

Every lesson so far that used a system prompt (Lessons 4, 9, 12) sent
it fresh on every single call, as part of `messages`. That's fine for
a program you control, but sometimes you want a model that's
*permanently* a certain persona or configuration, so that any call to
it, from any script, gets that behavior automatically, without every
caller having to remember to include the right system message.

A **Modelfile** does exactly that: it defines a new, named model built
on top of an existing one, with a system prompt and default parameters
baked in. It's the same idea as a Docker image built `FROM` a base
image with some setup already applied.

## The Modelfile format, briefly

Written to a text file and built with `ollama create <name> -f
Modelfile` on the CLI, a Modelfile looks like this:

```
FROM llama3.2
SYSTEM You are Pirate Pete, a pirate-themed coding assistant. Always answer in pirate speak, but keep technical accuracy intact.
PARAMETER temperature 0.7
```

`FROM` picks the base model, `SYSTEM` bakes in a fixed system prompt,
`PARAMETER` bakes in default `options` (Lesson 6). This lesson never
writes that file directly, `ollama.create()` takes the same three
pieces as Python keyword arguments instead, useful when you want a
program (not a human with a text editor) to define custom models.

## The code, piece by piece

```python
for _ in ollama.create(
    model=CUSTOM_MODEL_NAME,
    from_="llama3.2",
    system=SYSTEM_PROMPT,
    parameters={"temperature": 0.7},
):
    pass
```

`ollama.create()` streams progress updates as it builds the new model
(note `from_`, with a trailing underscore, since `from` is a reserved
Python keyword). The loop just drains that progress stream; a real
program might print or log each update instead of discarding it.

```python
response = ollama.chat(
    model=CUSTOM_MODEL_NAME,
    messages=[{"role": "user", "content": "What is a variable in programming?"}],
)
```

No system message in this call at all, and yet the reply comes back
fully in character. That's the entire point: the persona now lives on
the model itself, not in every caller's code.

```python
info = ollama.show(CUSTOM_MODEL_NAME)
system_line = next(line for line in info.modelfile.splitlines() if line.startswith("SYSTEM"))
```

`ollama.show()`, from Lesson 2, returns the model's full generated
Modelfile as text on `.modelfile`; the `SYSTEM` line inside it proves
the prompt really is stored on the model, not something this script
quietly re-sent.

```python
ollama.delete(CUSTOM_MODEL_NAME)
```

Same cleanup pattern as Lesson 7: this model was created just for the
lesson, so it's removed again at the end rather than left sitting on
disk.

## Running it

```bash
uv run python lessons/ollama/02_intermediate/16_custom_models_with_modelfile/lesson.py
```

## Expected output

```
Creating pirate-pete, built on llama3.2...

pirate-pete answering with no system message in this call:
Yer lookin' fer a variable, eh? Alright then, listen close, me hearty! A variable be a container fer storin' a value. Ye can think o' it like a treasure chest, where ye can stash a bit o' booty (data) and retrieve it later.
...

Baked-in system prompt, from ollama.show(): SYSTEM You are Pirate Pete, a pirate-themed coding assistant. Always answer in pirate speak, but keep technical accuracy intact.

Deleted pirate-pete.
```

The pirate-flavored answer's exact wording will vary between runs, but
it should always be both in-character and technically accurate, that
combination (persona plus correctness) is what the system prompt asks
for.

## Checkpoint

- **Modelfile**: defines a new named model `FROM` a base one, with a
  baked-in `SYSTEM` prompt and default `PARAMETER`s.
- **`ollama.create()`**: the Python equivalent of building a Modelfile,
  useful when a program (not a human) needs to define custom models.
- **Why bake it in**: a persona or configuration you'd otherwise have
  to remember to resend becomes automatic, for any caller.
- **`ollama.delete()`**: same cleanup habit as Lesson 7, remove models
  you created just for a demo.

If anything here still feels unclear, ask before moving to Lesson 17,
this tier's checkpoint project.
