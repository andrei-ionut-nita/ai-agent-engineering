# Lesson 18: Intermediate Checkpoint - A Multi-Turn Notes Assistant

## What this is

No new concepts in this lesson. This is a checkpoint: a small, real
script built entirely out of ideas from Lessons 10 through 17, combined
into one thing. If you can read `lesson.py` and understand why every
piece is there, you've mastered the Intermediate tier. If any piece
feels unfamiliar, that's a sign to revisit the lesson it came from
before continuing to Advanced.

## What it does

Runs a four-question conversation, a fixture question, a general
knowledge question, a follow-up that depends on the first question's
context, and a compound fixture question, printing each turn's answer,
then saves the whole structured transcript to disk.

## Where each piece came from

```python
def ask_turn(contents: list[types.Content], query: str, store: list[dict]) -> str:
    contents.append(types.Content(role="user", parts=[types.Part(text=query)]))
    for _ in range(MAX_STEPS): ...
```
Lesson 13's session-turn shape (mutating a shared `contents` list
across calls) combined with Lesson 14's `MAX_STEPS` bound, so a single
question in the conversation can never run away indefinitely.

```python
def run_tool_safe(call: types.FunctionCall, store: list[dict]) -> dict[str, str]:
    try:
        ...
        return {"output": search_notes(args["query"], store)}
    except Exception as error:
        return {"error": f"{type(error).__name__}: {error}"}
```
Lesson 16's failure-mode handling: any malformed call or tool exception
becomes an `{"error": ...}` function response instead of crashing the
whole conversation.

```python
SYSTEM_INSTRUCTION = """... cite the source file ... Only call
search_notes for questions about the personal notes collection ..."""
```
Lesson 15's citation instruction and Lesson 6's "don't retrieve
unnecessarily" steering, combined into one standing instruction for the
whole session.

```python
save_history(contents, HISTORY_PATH)
load_history(HISTORY_PATH)
```
Lesson 13, unchanged: the entire structured transcript persisted to and
reloadable from JSON.

## Running it

```bash
uv run python lessons/agentic_rag/02_intermediate/18_intermediate_checkpoint_project/lesson.py
```

You should see: the sourdough question answered from
`sourdough-starter.md` with a citation, the gold question answered
directly with no retrieval, the acetone follow-up correctly resolving
"it" from the first turn's context (possibly without needing a fresh
`search_notes` call at all, since the relevant fact may already be in
the transcript), and the pedalboard question answered with a citation
to `guitar-pedalboard.md`.

## Try this yourself

Without looking anything up:

- Delete `conversation_history.json` and run the script twice in a row
  without clearing it between runs (comment out the `HISTORY_PATH.unlink()`
  line in `main()` temporarily). Does the second run's first answer
  behave any differently, now that four unrelated turns from the first
  run are already sitting in its loaded history?
- Add a fifth question to `conversation` that's deliberately ambiguous
  between general knowledge and the notes collection (see Lesson 16's
  discussion of this). Watch whether it retrieves unnecessarily, then
  decide whether `SYSTEM_INSTRUCTION` needs to be more specific.
- Trigger Lesson 16's malformed-call failure for real here: temporarily
  change `run_tool_safe()`'s `args["query"]` to `args["nonexistent_key"]`
  and rerun. Does the conversation recover and keep going, or does
  something break? What does that tell you about how thoroughly
  `run_tool_safe()` actually isolates the rest of the loop from a bad
  call?

If you can make these changes confidently, you're ready for the
Advanced tier, starting at Lesson 19.
