# Lesson 13: Persisting Conversation History

## Where we left off

Every lesson so far built `contents` fresh at the start of `main()` and
threw it away when the script ended. A real assistant needs to survive
restarts, a user closing a terminal and reopening it later, a server
process being redeployed, without forgetting what was already asked.
This lesson saves the entire structured transcript, questions, tool
calls, and tool results alike, to disk, and reloads it into a working
session.

## The code, piece by piece

```python
def save_history(contents: list[types.Content], path: Path) -> None:
    raw = [content.model_dump(mode="json") for content in contents]
    path.write_text(json.dumps(raw, indent=2))
```

`google-genai`'s `types` build on `pydantic.BaseModel`, so every
`Content`, and everything nested inside it (`Part`, `FunctionCall`,
`FunctionResponse`), already knows how to serialize itself to plain
JSON via `model_dump(mode="json")`. Nothing about function calls needed
special-casing here, it's a direct consequence of Lesson 12's insight:
`contents` is a structured object, and pydantic models serialize
structure for free.

```python
def load_history(path: Path) -> list[types.Content]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text())
    return [types.Content.model_validate(item) for item in raw]
```

`Content.model_validate()` is the reverse direction, plain JSON back
into real `Content` objects Gemini's SDK expects. An empty or missing
file returns an empty history, a fresh session, exactly the shape a
real assistant's first-ever run needs.

```python
reloaded_contents = load_history(HISTORY_PATH)
answer = ask_turn(reloaded_contents, "What about it makes it smell like acetone?", store)
```

The demo deliberately simulates a restart: `main()` saves after turn
one, then calls `load_history()` again as if starting a brand new
process, and asks a follow-up question that only makes sense with turn
one's context still present ("it" refers to the starter, established
two questions ago).

## Why this has to be the whole `contents` list, not just a Q&A log

A tempting shortcut is to persist only the final question/answer pairs,
a plain list of `{"question": ..., "answer": ...}` dicts, since that's
"the part a human cares about." That throws away exactly the structure
Lesson 12 showed is load-bearing: which tool was called, with what
arguments, and what it returned. Reloading only Q&A pairs and replaying
them as plain text would mean re-deriving the model's own past
reasoning from scratch every session, defeating the purpose.

## Running it

```bash
uv run python lessons/agentic_rag/02_intermediate/13_persisting_conversation_history/lesson.py
```

## Expected output

```
Turn 1 (fresh session, no history on disk):
  A: The sourdough starter needs feeding every 12 hours at room temperature.
  Saved 3 turns to conversation_history.json

Turn 2 (reloaded 3 turns from disk, a new process could do this):
  A: Skipping a feeding at room temperature for more than a day makes it smell sharply of acetone, a sign it's hungry.
```

Turn count may vary slightly depending on whether the model called
`search_notes` once or needed a second lookup.

## Checkpoint

- `Content.model_dump(mode="json")` / `Content.model_validate(...)`
  round-trip a full tool-calling transcript through JSON, because
  `google-genai`'s types are pydantic models.
- Persisting the structured `contents` list (not a flattened Q&A log)
  is what lets a reloaded session correctly resolve a pronoun like
  "it" from two turns ago.
- **Try this yourself**: open `conversation_history.json` after running
  this lesson and find the `function_call` and `function_response`
  parts inside it. Can you identify, just from reading the file, which
  question triggered the tool call and what it returned?

If anything here still feels unclear, ask before moving to Lesson 14.
