# Lesson 10: run_flow_from_json in depth

## Where we left off

Beginner used `run_flow_from_json` as a black box: hand it a `flow.json`
and an `input_value`, get an answer back. It has one more feature worth
knowing before Intermediate moves on to the REST API: **tweaks**,
overriding a component's field for a single run without editing the
`flow.json` file on disk.

## Why this matters

A shipped `flow.json` is meant to be a stable, reviewable artifact,
exactly like a config file. Editing it every time you want to try a
different system prompt defeats that. `tweaks` gives you the same
one-off override you'd get from typing into a component's field on the
canvas and clicking Run, but from code, scriptable, and without ever
touching the file.

## Do this yourself

1. Open `flow.json` in this folder (or reopen the Lesson 2 flow, they're
   the same shape: Chat Input -> Google Generative AI -> Chat Output).
2. Find the Google Generative AI component's **System Message** field in
   the canvas, type something like "Answer only in pirate speak", run it
   in the Playground, confirm the tone changes.
3. Clear that field back out. The `tweaks` dict in `lesson.py` does the
   exact same override, but only for one Python call, the file (and the
   canvas, if you reload it) goes right back to its original system
   message afterward.

## The code, piece by piece

```python
GEMINI_COMPONENT_ID = "GoogleGenerativeAIComponent-lesson10"
gemini._id = GEMINI_COMPONENT_ID
```

`tweaks` targets a component by its `id`, the same id visible in
`flow.json`'s `data.nodes[].id`. Every component gets a random suffix by
default (`GoogleGenerativeAIComponent-a2YHI`, different every time you
build the graph), so this lesson pins a fixed, readable id right after
constructing the component, before wiring it into anything, so the id in
`flow.json` matches the id used in `tweaks` below.

```python
run_flow_from_json(
    flow=str(FLOW_PATH),
    input_value=question,
    tweaks={GEMINI_COMPONENT_ID: {"system_message": "Answer only in pirate speak."}},
)
```

The dict's keys are component ids, its values are `{field_name: new_value}`
overrides for that component. Any field the component has can be
tweaked this way, not just `system_message`, `model_name` or
`temperature` work exactly the same. The override only applies to this
one `run_flow_from_json` call, `flow.json` on disk is never modified.

## Running it

```bash
uv run python lessons/langflow/02_intermediate/10_run_flow_from_json_in_depth/lesson.py
```

## Expected output

Approximate, Gemini's exact phrasing varies, but the second answer
should be in pirate speak and the first shouldn't:

```
Default system message:
Choosing a name for a goldfish is a fun tradition! ...

Tweaked system message (pirate):
Ahoy, matey! If ye be seekin' a proper moniker fer yer scaly, orange-bellied swabbie ...
```

## Checkpoint

- **`tweaks`**: a `{component_id: {field: value}}` dict, overrides a
  component's field for one `run_flow_from_json` call, the flow file on
  disk is never touched.
- **component `id`**: what `tweaks` targets, visible in `flow.json`'s
  `data.nodes[].id`, and pinnable in code via `component._id` before
  wiring it into a graph.

If anything here still feels unclear, ask before moving to Lesson 11.
