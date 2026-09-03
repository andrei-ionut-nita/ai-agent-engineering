# Lesson 12: Passing Tool Results Back Correctly

## Where we left off

Every lesson since Lesson 5 has included this exact line, without much
comment:

```python
contents.append(response.candidates[0].content)
```

This lesson finally explains why it can't be skipped, by skipping it on
purpose and watching what happens.

## The misconception this lesson corrects

The tempting shortcut is: "the model asked for `search_notes`, I ran it,
now I just need to tell the model the result, so I'll add a turn with
the result and call `generate_content()` again." That reasoning treats
the function *result* as the only thing that matters and the function
*call* as disposable scaffolding you already handled. It isn't. Gemini's
function-calling contract expects every `function_response` turn to
immediately follow the exact `function_call` turn it's answering, so
the model can match "here's what I asked for" to "here's what I got"
inside its own conversation history. Omitting the call turn breaks that
matching.

## The code, piece by piece

```python
def broken_ask(query: str, store: list[dict]) -> str:
    ...
    # Missing: contents.append(response.candidates[0].content)
    contents.append(types.Content(role="user", parts=[types.Part.from_function_response(...)]))
```

`broken_ask()` does everything `correct_ask()` does except the one
line: it never appends the model's own turn (the one containing the
`function_call` part) before attaching the function's result. The
`contents` list it sends looks like: user asks question, user provides
a function's result, with no record of any call ever having been
requested in between.

```python
except errors.APIError as error:
    print(f"  Failed as expected: {error.code} {error.status} - {error.message}\n")
```

Gemini's API rejects this shape outright, `google.genai.errors.APIError`
is the SDK's exception for API-level errors, carrying the HTTP-style
`code`, a `status` string, and a human-readable `message`. This isn't a
Python bug, it's the API refusing a malformed request, the same kind of
signal Lesson 16 studies more generally for any tool call that comes
back malformed.

## Why this matters beyond just avoiding an error

The deeper lesson isn't "remember this one line," it's that a
multi-turn tool-calling conversation is a *structured transcript*, not
a growing string. Every turn has a role and a specific part type
(`text`, `function_call`, `function_response`), and the model relies on
that structure to track its own reasoning across turns. Lesson 13's
persistence lesson depends on this same insight: what gets saved and
reloaded is the structured `contents` list, not a flattened summary of
it.

## Running it

```bash
uv run python lessons/agentic_rag/02_intermediate/12_passing_tool_results_back_correctly/lesson.py
```

## Expected output

```
Q: How often does the vinyl turntable's belt need replacing?

Trying broken_ask() (skips the model's own function_call turn)...
  Failed as expected: 400 INVALID_ARGUMENT - <a message about a function_response with no matching function_call>

Trying correct_ask() (replays the model's own turn first)...
  A: The turntable's belt gets replaced roughly once a year, sooner if the platter's speed sounds off.
```

Some SDK/API combinations tolerate the missing `function_call` turn
instead of rejecting it outright. If `broken_ask()` prints "Unexpectedly
succeeded" instead of "Failed as expected", that's `lesson.py`'s own
fallback branch, not a bug: treat that success as luck, not
correctness. The API's willingness to accept a malformed history
doesn't make replaying the model's own turn optional, `correct_ask()`
is still the only version this lesson recommends.

## Checkpoint

- A tool-calling conversation is a structured list of `Content` turns,
  not a string being concatenated.
- `response.candidates[0].content` (the model's own function-call turn)
  must be replayed back before the matching `function_response` turn,
  skipping it produces an API error, not a quietly wrong answer.
- `google.genai.errors.APIError` (`.code`, `.status`, `.message`) is
  this SDK's exception type for a request the API itself rejects.

If anything here still feels unclear, ask before moving to Lesson 13.
