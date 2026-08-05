# Lesson 10 (Checkpoint): Notes Server

## What this combines

Nothing new here, this is where the beginner tier's pieces meet:

- **Tools** (Lessons 2-4): `add_note`, `list_notes`, `delete_note`,
  functions that change server state.
- **Resources** (Lesson 5): `notes://{note_id}`, read a specific note's
  content without "doing" anything.
- **Prompts** (Lesson 6): `summarize_notes`, a template asking a model
  to summarize everything currently stored.
- **Error handling** (Lesson 7): `delete_note` raises a clear error if
  the note doesn't exist, rather than silently doing nothing.
- **Logging** (Lesson 8): all internal bookkeeping goes through
  `logging`, never `print()`.

## The design

`server.py` keeps notes in a plain Python dict, in memory, keyed by an
auto-incrementing id. This mirrors the `lifespan`/shared-state pattern
Lesson 18 will formalize later, for now, module-level state is enough:

```python
_notes: dict[int, str] = {}
_next_id = 1


@mcp.tool()
def add_note(text: str) -> int:
    """Add a note and return its id."""
    global _next_id
    note_id = _next_id
    _notes[note_id] = text
    _next_id += 1
    return note_id
```

## Running it

`lesson.py` acts as the client: it adds a few notes, lists them, reads
one back as a resource, asks for the summarize-notes prompt, then
deletes a note and shows the error you get from deleting one that
doesn't exist.

```bash
uv run python lessons/mcp/01_beginner/10_beginner_checkpoint_project/lesson.py
```

You can also point the Inspector at `server.py` directly and poke
around by hand:

```bash
npx @modelcontextprotocol/inspector \
    uv run python lessons/mcp/01_beginner/10_beginner_checkpoint_project/server.py
```

## Checkpoint

If this lesson ran cleanly and made sense without looking anything up,
you're ready for the intermediate tier: connecting a client to your
own server is exactly what Lesson 11 does next, except this time you
already know what's on the other end of the connection, because you
just built it.

If anything here still feels unclear, go back to whichever of Lessons
2-9 covered that piece before moving to Lesson 11.
