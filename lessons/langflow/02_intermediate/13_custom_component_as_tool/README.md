# Lesson 13: a Custom Component as a Tool

## Where we left off

Lesson 12's `TitleCaseComponent` had exactly one place it could go, wired
directly into the next component's input, always run, every time. A
tool is different: it's offered to an **Agent**, which decides for
itself, per request, whether to call it at all. This lesson writes the
same kind of Custom Component again, but shaped to be a tool instead of
a fixed step in the chain.

## Why this lesson runs the graph directly

Same reason as Lesson 12: `graph.arun()` runs the in-memory graph
without any JSON deserialization step, so the migration-loop bug from
Lesson 2 (triggered only by loading an unrecognized component type from
JSON) never enters the picture. `flow.json` here is for reference only,
not for reloading through `run_flow_from_json` or the REST API.

## Do this yourself

1. Build on Lesson 4's flow (Google Generative AI already on the
   canvas) or start fresh: **Chat Input**, **Google Generative AI**,
   and an **Agent** component (search "Agent" in the sidebar).
2. Connect Google Generative AI's **Model** output (not its **Message**
   output, a different port, this one has type `LanguageModel`) into
   the Agent's **Model** input. This is a different wiring than every
   earlier lesson, the Agent consumes a model as a connection, not a
   typed-in name.
3. Add a **New Custom Component** the same way as Lesson 12, paste in
   `WordLengthTool` from `lesson.py` below. Connect its **Tool** output
   into the Agent's **Tools** input.
4. Connect Chat Input into the Agent's **Input** field, and the Agent's
   **Response** output into a **Chat Output**.
5. In the Playground, ask something like "how many letters are in
   'xylophone'?" and something unrelated like "what's the capital of
   France?". Watch the Agent's own reasoning trace in the Playground,
   it should call the tool for the first question and answer directly
   for the second.

No `canvas.png` ships with this lesson: re-importing a saved flow that
wires a model into an Agent's **Model** field this way, rather than
connecting it by hand on the canvas, trips a frontend validation quirk
in this Langflow version, the import silently drops that one edge and
shows "Some connections were removed because they were invalid." The
flow still runs correctly (verified via `lesson.py` and the REST API,
this is purely a re-import display quirk), but a screenshot produced
that way would show the Agent's Model input disconnected, which
would be actively misleading here. Build it by hand following the
steps above and it wires and runs exactly as described.

## The code, piece by piece

```python
def build_tool(self) -> Tool:
    from langchain_core.tools import StructuredTool
    ...
    return StructuredTool.from_function(
        name="word_length",
        description="Return the number of characters in a single word.",
        func=_word_length,
        args_schema=WordLengthSchema,
    )
```

Lesson 12's output method returned a `Message`, meant to feed straight
into the next component. This one returns a LangChain `Tool` object,
meant to be handed to an Agent, which reads its `name` and
`description` to decide when it's relevant, the same object you'd build
if you were writing this tool for a raw LangChain agent with no
Langflow involved at all.

```python
agent.set(
    model=gemini.build_model,
    tools=[word_length.build_tool],
    ...
)
```

`model=gemini.build_model` connects the Google Generative AI
component's model output, not its text output, into the Agent, this is
what lets the Agent do its own reasoning and tool-calling with that
model. `tools=[word_length.build_tool]` is a list, an Agent can be
given several tools this way, each entry another component's tool
output method.

## Running it

```bash
uv run python lessons/langflow/02_intermediate/13_custom_component_as_tool/lesson.py
```

No running Langflow server is required for this one. Agent calls
involve more than one round trip to Gemini (deciding whether to call a
tool, running it, then writing the final answer), so this lesson is
noticeably slower than earlier ones, 20-60 seconds isn't unusual.

## Expected output

Approximate, Gemini's exact phrasing varies, but the number should be
correct:

```
Agent said: The word 'xylophone' has 9 letters.
```

## Checkpoint

- **tool-shaped output**: a Custom Component output method that returns
  a `Tool` object instead of a `Message`, meant to be offered to an
  Agent, not wired as a fixed step.
- **Agent's `model` input**: a connection, not a typed-in name, wired
  from another component's model-typed output (`build_model`, not
  `text_response`).
- **the Agent decides**: unlike every earlier flow's fixed chain, the
  Agent chooses per request whether to call a given tool at all.

If anything here still feels unclear, ask before moving to Lesson 14.
