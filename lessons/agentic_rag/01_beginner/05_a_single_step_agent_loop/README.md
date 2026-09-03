# Lesson 5: A Single-Step Agent Loop

## Where we left off

Lesson 4 stopped right after printing the tool's raw result, a chunk of
retrieved text, not an answer. This lesson closes the loop: hand that
result back to Gemini so it can turn raw retrieved text into an actual
answer to the original question. This is the smallest complete "agent
loop" this course will build: at most one round trip, model, then tool
(if requested), then model again.

## The code, piece by piece

```python
contents: list[types.Content] = [types.Content(role="user", parts=[types.Part(text=query)])]
response = client.models.generate_content(model=CHAT_MODEL, contents=contents, config=CONFIG)
```

Every earlier lesson passed a plain string as `contents`. Multi-turn
function calling needs the list form instead, because the model's
function-call request and your tool's result both need to become
turns of their own before Gemini can see them together. `types.Content(role=..., parts=[...])`
is that turn: `role="user"` for anything you or a tool provide,
`role="model"` for anything Gemini said.

```python
assert response.candidates is not None
contents.append(response.candidates[0].content)
```

`response.candidates[0].content` is already a complete `Content` object
representing the model's own turn, containing the `function_call` part
`response.function_calls` extracted a shortcut view of. Appending it
directly (rather than reconstructing it by hand) is what makes the next
call's `contents` list an accurate transcript: user asked, model
requested a call, here's the result, in that order.

```python
contents.append(
    types.Content(
        role="user",
        parts=[types.Part.from_function_response(name=call.name, response={"result": result})],
    )
)
```

`Part.from_function_response()` wraps the tool's return value (a plain
string here) into the shape Gemini expects a function's result to
arrive in, a dict under the `response` key. The `role="user"` here is
not a typo: from the API's perspective, a tool result is something
*given to* the model, the same conceptual role as the original
question, even though your own code produced it, not a person typing.

```python
final_response = client.models.generate_content(model=CHAT_MODEL, contents=contents, config=CONFIG)
return final_response.text or ""
```

The second call sends the *entire* transcript so far, question, the
model's own call request, and the tool's result, back to Gemini. This
is what turns "here is a raw retrieved passage" into "here is a
grounded, worded answer to your original question." Skipping this
second call is a common mistake: without it, you have retrieved text,
not an answer.

## Why this shape, not "just call the tool directly"

It would be simpler to skip Gemini's request entirely: embed the
question, search, generate an answer, exactly what
`fixed_pipeline_ask()` in Lesson 2 already did. The reason not to is
the whole point of this course: that shortcut retrieves *unconditionally*.
This loop only calls `search_notes()` when the model, reading the
specific question, decides it needs to. Lesson 6 makes that decision
visible by asking a question where the model decides *not* to call it.

## Running it

```bash
uv run python lessons/agentic_rag/01_beginner/05_a_single_step_agent_loop/lesson.py
```

## Expected output

```
Q: How often does Clarence the sourdough starter need feeding at room temperature?
A: Clarence needs feeding every 12 hours at room temperature.
```

## Checkpoint

- **`ask(query, store)`**: model call, tool call if requested, tool
  result handed back, final model call, the complete single-step loop.
- `types.Content(role=..., parts=[...])` turns build the conversation
  transcript Gemini needs to see the tool result in context.
- `response.candidates[0].content` is the model's own turn, append it
  verbatim rather than reconstructing it.
- `Part.from_function_response()` is the correct shape for a tool's
  result; skipping the second `generate_content()` call leaves you with
  raw retrieved text, not a real answer.

If anything here still feels unclear, ask before moving to Lesson 6.
