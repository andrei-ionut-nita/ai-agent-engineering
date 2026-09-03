# Lesson 4: Retrieval as a Tool

## Where we left off

Lesson 3's `get_current_temperature` tool was a placeholder, a
`FunctionDeclaration` describing a function that never actually ran.
This lesson swaps it for a real one: `search_notes()`, everything
`naive_rag`'s `retrieve()` already does, embed the query, rank fixture
notes by cosine similarity, keep the top `k`, wrapped so it can be
declared as a tool and genuinely executed once the model asks for it.

## The code, piece by piece

```python
def search_notes(query: str, store: list[dict], k: int = 2) -> str:
    ...
    return "\n\n---\n\n".join(f"[{r['source']}]\n{r['text']}" for r in top_k)
```

Same retrieval math every earlier course used, cosine similarity over
embedded fixture notes, with one change: it returns a plain string
instead of a list of dicts. Tool results eventually get handed back to
Gemini as text (Lesson 5), so `search_notes()` does that formatting
itself, tagging each passage with its source file, rather than leaving
formatting to whatever calls it.

```python
SEARCH_NOTES_DECLARATION = types.FunctionDeclaration(
    name="search_notes",
    description=(
        "Search a personal notes collection (...) for passages relevant "
        "to a query. Use this only for questions about these specific "
        "personal topics, not for general knowledge questions."
    ),
    ...
)
```

The description here is doing real work, it's the only information the
model has about *when* to reach for this tool. Naming the five topics
covered and explicitly steering away from general-knowledge questions
is what gives the model a fighting chance at Lesson 6's job: correctly
declining to call this tool when it isn't needed.

```python
result = search_notes(call.args["query"], store)
```

This lesson still does the "actually run the function" step by hand,
one `if` branch, one call. That's deliberately not yet a general loop,
seeing it done manually once, for one tool, makes Lesson 5's loop
version legible instead of magic.

## Why the model's chosen query matters

Watch what `call.args["query"]` actually contains when you run this:
it's often not a verbatim copy of the original question. Gemini
frequently rewrites it into something closer to what the notes
themselves would use ("sourdough starter feeding schedule" instead of
"How often does Clarence need feeding"). That's the model doing its own
lightweight query optimization, for free, as a side effect of deciding
what to search for, something the fixed pipeline's `retrieve(query, ...)`
never had the chance to do because `query` was always just the original
question, verbatim.

## Running it

```bash
uv run python lessons/agentic_rag/01_beginner/04_retrieval_as_a_tool/lesson.py
```

## Expected output

```
Q: How often does Clarence the sourdough starter need feeding at room temperature?

Gemini requested: search_notes(query='sourdough starter feeding schedule')

search_notes() actually returned:
[sourdough-starter.md]
# Sourdough Starter
...
```

## Checkpoint

- `search_notes()` is retrieval unchanged, just returning a formatted
  string instead of a list of scored dicts, so it can go straight into
  a tool result.
- The tool's `description` is the model's only signal for *when* to use
  it, vague or missing descriptions produce unreliable tool-choice
  behavior later in this course.
- The model can (and often does) rewrite the query before searching,
  something the old fixed pipeline never allowed.
- **Try this yourself**: change the description to remove the "use this
  only for..." sentence, then rerun both this lesson and, once you
  reach it, Lesson 6's general-knowledge question through the same
  tool. Does removing that steering sentence change whether the model
  reaches for the tool when it shouldn't?

If anything here still feels unclear, ask before moving to Lesson 5.
