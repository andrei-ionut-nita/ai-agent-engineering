# Lesson 14: the Agent component's built-in tools

## Where we left off

Lesson 13 gave an Agent a custom tool you wrote yourself. Most of the
time you don't need to, Langflow's own **Agent** component ships two
tools as checkboxes, a calculator and a current-date lookup, no code at
all. This lesson is the plain version: same Agent, same wiring, no
Custom Component in sight.

## Do this yourself

1. Build **Chat Input**, **Google Generative AI**, and **Agent**, wire
   Google Generative AI's **Model** output into the Agent's **Model**
   input (Lesson 13's connection, a model-typed port, not the message
   one), Chat Input into the Agent's **Input**.
2. Open the Agent's settings. Find **Current Date** and **Calculator**
   toggles (under the tools section) and turn both on. No Custom
   Component, no wiring, a checkbox each.
3. Wire the Agent's **Response** into a **Chat Output**.

No `canvas.png` ships with this lesson: re-importing a saved flow that
wires a model into an Agent's Model field this way trips a frontend
re-import quirk in this Langflow version, the edge gets silently
dropped with an "invalid connections" notice, even though the flow
runs correctly (verified via `lesson.py`). Build it by hand following
the steps above and the wiring holds.
4. In the Playground, ask something that needs both: "what is 47 times
   6, and what's today's date?" Confirm both parts of the answer are
   correct, the date one especially, since that's not something the
   model would know on its own.

## The code, piece by piece

```python
agent.set(
    model=gemini.build_model,
    add_calculator_tool=True,
    add_current_date_tool=True,
    ...
)
```

`add_calculator_tool` and `add_current_date_tool` are plain boolean
fields on `AgentComponent`, the code-equivalent of the two toggles from
step 2. No `tools=[...]` list needed for these, since they're not
separate components at all, just built into the Agent itself.

```python
result = run_flow_from_json(flow=str(FLOW_PATH), input_value="What is 47 times 6, and what's today's date?")
```

Back to `run_flow_from_json`, same as every lesson before 12-13. Unlike
those two, nothing here involves a Custom Component, so there's no
JSON-deserialization risk to route around, this flow loads and runs
completely normally.

## Running it

```bash
uv run python lessons/langflow/02_intermediate/14_agent_component/lesson.py
```

Same as Lesson 13, an Agent call involves more than one round trip to
Gemini, so give it a little longer than the single-model lessons.

## Expected output

Approximate, Gemini's exact phrasing varies, but both facts should be
correct:

```
Agent said: 47 times 6 is 282, and today's date is August 19, 2026.
```

## Checkpoint

- **built-in Agent tools**: `add_calculator_tool` / `add_current_date_tool`,
  boolean fields, no Custom Component or wiring required, the
  lowest-effort way to give an Agent a capability.
- **when to reach for a Custom Component instead** (Lesson 13): once
  the tool needs to do something Langflow doesn't already ship, your
  own API call, your own business logic.

If anything here still feels unclear, ask before moving to Lesson 15.
