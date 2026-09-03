# Lesson 9: Beginner Checkpoint - A CLI Assistant That Decides

## What this is

No new concepts in this lesson. This is a checkpoint: a small, real
script built entirely out of ideas from Lessons 1 through 8, combined
into one thing. If you can read `lesson.py` and understand why every
piece is there, you've mastered the Beginner tier. If any piece feels
unfamiliar, that's a sign to revisit the lesson it came from before
continuing to Intermediate.

## What it does

Embeds all five fixture notes once, then answers four questions in a
row, one needing retrieval, one needing the time tool, one needing
neither, and one more needing retrieval again, printing which tool (if
any) the model reached for isn't shown explicitly here the way Lesson
8 showed it, deliberately, this checkpoint reads like something you'd
actually hand a user: just questions and answers, the tool routing
invisible because it's supposed to be.

## Where each piece came from

```python
store = build_vector_store()
```
Lessons 2, 4: embed every fixture note once, up front, the expensive
step that should only happen once per run.

```python
TOOLS = types.Tool(function_declarations=[SEARCH_NOTES_DECLARATION, GET_CURRENT_DATETIME_DECLARATION])
CONFIG = types.GenerateContentConfig(tools=[TOOLS])
```
Lesson 7: both tools declared together, so the model can pick between
them (or neither) per question.

```python
def run_tool(call: types.FunctionCall, store: list[dict]) -> str:
    if call.name == "search_notes": ...
    elif call.name == "get_current_datetime": ...
```
Lesson 7's dispatch, unchanged: match the model's requested tool name
to the real function that implements it.

```python
def ask(query: str, store: list[dict]) -> str:
    ...
```
Lesson 5's loop shape, Lesson 6's "sometimes there's no call at all"
branch, Lesson 7's multi-tool dispatch, all in one function: model
call, tool call if requested, tool result handed back, final answer.

## Running it

```bash
uv run python lessons/agentic_rag/01_beginner/09_beginner_checkpoint_project/lesson.py
```

You should see the pedalboard question answered from
`guitar-pedalboard.md`, the New York question answered with a live
timestamp, the kilometer/mile question answered directly with no tool
call, and the vinyl question answered from `vinyl-collection.md`, four
different routing decisions, one function.

## Try this yourself

Without looking anything up:

- Add a third tool of your own, something as trivial as
  `get_current_datetime()` was (a word-counter, a Celsius-to-Fahrenheit
  converter, anything needing no new dependency). Declare it, add a
  branch to `run_tool()`, and ask a question only it can answer. Does
  the model reach for it correctly on the first try?
- Ask a question that's genuinely ambiguous between the notes tool and
  general knowledge, for example "What's a good daily routine for
  learning a skill?" (it could answer generically, or pull from
  `language-journal.md`). Which way does it go, and does the tool's
  `description` explain why?
- Remove `get_current_datetime` from `TOOLS` entirely (leave the
  function and its branch in `run_tool()` in place) and re-ask the New
  York time question. What does the model do when a tool it would have
  used is no longer declared? This previews Lesson 16's failure-modes
  lesson: a model can't call a tool it doesn't know exists, and its
  fallback behavior when that happens is worth seeing on purpose.

If you can make these changes confidently, you're ready for the
Intermediate tier, starting at Lesson 10.
