# Lesson 3: components as typed contracts

## Where we left off

Lesson 2 connected three components by dragging lines between dots. This
lesson is about what those dots actually are: not just a visual nicety,
but a type contract, the same idea as a Python function's type hints,
made visible.

## Do this yourself

You don't need a new flow for this, reopen the one from Lesson 2 (still
in your Langflow tab, or reachable from the flows dashboard).

1. Click the Google Generative AI component's title to open its
   settings, or hover it and click the wrench/settings icon, and toggle
   **Advanced** on so every field shows, including **Temperature**.
2. Try to drag a connection from Chat Input's output dot to the
   Temperature field. Notice the canvas either won't offer that dot as
   a valid drop target at all, or refuses to complete the connection,
   the same rejection `lesson.py` below triggers in code.
3. Drag a connection from Chat Input's output dot to the **Input**
   field instead (the one already connected from Lesson 2), notice it's
   colored to match, and the connection completes cleanly.

## Ports have types, not just names

Every component declares two things per port: what type of value it
**produces** (an output's `types`) and what types it's willing to
**accept** (an input's `input_types`). `ChatInput`'s message output
produces a `Message`, an object carrying text, sender, and metadata,
not a raw string. The Google Generative AI component's `input_value`
field declares `input_types=['Message']`, so it accepts exactly that.
The canvas reads these same declarations to decide which dots are
allowed to connect to which, that's why dragging a valid connection
lights the target port up and dragging an invalid one doesn't.

## Not every field is a port

Its `temperature` field has no `input_types` at all, on the canvas it
renders as a plain slider, not a connectable dot, because nothing
declared it connectable. This is a deliberate, useful distinction: some
values (temperature, a model name) are meant to be configured once when
you build the flow, others (the message itself) are meant to flow
through it at runtime. A component's author decides which is which by
whether they give a field `input_types`.

## The code, piece by piece

```python
for field in gemini.inputs:
    input_types = getattr(field, "input_types", None)
    if input_types:
        print(f"Google Generative AI input {field.name!r} only accepts: {input_types}")
```

This reads the exact same declarations the canvas reads. `input_value`
and `system_message` both declare `input_types=['Message']`,
`temperature` doesn't show up in this loop at all, it has no declared
`input_types`, matching what you saw as "not a connectable dot" in the
browser.

```python
bad_gemini.set(temperature=bad_input.message_response)
...
try:
    Graph(start=bad_input, end=bad_output)
except ValueError as e:
    print(f"Invalid connection (Message -> Temperature) rejected: {e}")
```

`.set()` itself doesn't check types, it just stores the value, that's
why this line doesn't fail immediately. The contract is enforced when
`Graph(...)` assembles the whole flow and has to turn every `.set()`
call into a real edge: it looks up `temperature`'s declared
`input_types`, finds none, and refuses to build an edge to it at all.
Same rule, same rejection, whether you tried it by dragging or by code.

## Running it

```bash
uv run python lessons/langflow/01_beginner/03_components_as_contracts/lesson.py
```

## Expected output

Exact, no model call happens in this lesson:

```
Google Generative AI input 'input_value' only accepts: ['Message']
Google Generative AI input 'system_message' only accepts: ['Message']
Valid connection (Message -> Input): graph builds fine.
Invalid connection (Message -> Temperature) rejected: Component Google Generative AI field 'temperature' might not be a valid input.
```

## Checkpoint

- **output `types`**: what kind of value a port produces (`ChatInput`'s
  `message` output produces a `Message`).
- **input `input_types`**: what kinds of value a port will accept, a
  field without any isn't a connectable port at all, just a
  configuration value.
- **the contract is enforced at graph-build time**, not when you call
  `.set()`, whether you're dragging on the canvas or wiring in Python,
  the same check runs.

If anything here still feels unclear, ask before moving to Lesson 4.
