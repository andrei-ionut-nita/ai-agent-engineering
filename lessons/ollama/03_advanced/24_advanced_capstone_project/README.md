# Lesson 24 (Capstone): Fully Offline RAG Agent

## What this combines

Every idea from this course, in one program:

- **Readiness checking** (Lesson 22): `wait_for_ollama()` runs before
  anything else, so a cold-started Ollama service doesn't cause a
  confusing crash.
- **RAG, as a tool** (Lesson 21): the split/embed/retrieve pipeline is
  built once into a `NotesIndex`, then exposed to the model as a
  `search_notes` tool, rather than always running unconditionally on
  every question. The model itself decides when a question actually
  needs the notes.
- **Multi-tool calling loop** (Lesson 17): `search_notes` and
  `calculate` both available at once, dispatched through the same
  `functions` dict pattern.
- **Real multi-turn memory** (Lesson 12): one growing `messages` list
  across two related questions, the second only answerable using the
  first's result.
- **Streaming** (Lesson 5): the model's final, natural-language answer
  streams live; only the (much shorter) tool-call decision is a single
  non-streamed chunk, since Ollama doesn't stream those token by token.

And, underneath everything, the whole course's throughline: `.env`
never even gets imported here. No API key, no cloud call, at any point.

## Why RAG as a tool, not a fixed step

Lesson 21 always ran retrieval before generation, every question got a
context chunk whether it needed one or not. This capstone makes that a
choice: `search_notes` is offered as a tool alongside `calculate`, and
the model decides, per question, whether it needs the notes at all.
That's a closer match to a real assistant, which fields plenty of
questions (chit-chat, general knowledge, pure arithmetic) that have
nothing to do with any specific knowledge base.

## The code, piece by piece

```python
class NotesIndex:
    def __init__(self, path: Path):
        text = path.read_text()
        splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
        self.chunks = splitter.split_text(text)
        self.embeddings = ollama.embed(model="nomic-embed-text", input=self.chunks).embeddings

    def search(self, query: str) -> str:
        ...
```

Splitting and embedding happen once, in `__init__`, not on every
search. This mirrors why the pgvector course stores embeddings in a
real database instead of recomputing them per query: the expensive
work (embedding every chunk) should happen once, searches after that
are cheap.

```python
stream = ollama.chat(model=MODEL, messages=messages, tools=tools, stream=True)
content = ""
tool_calls = []
for chunk in stream:
    if chunk.message.tool_calls:
        tool_calls = chunk.message.tool_calls
    if chunk.message.content:
        print(chunk.message.content, end="", flush=True)
        content += chunk.message.content
```

Streaming and tool calling, combined: every call streams, but a
tool-requesting response arrives as one early chunk carrying the full
`tool_calls` list (Ollama doesn't stream a decision to call a tool
token by token), while a direct answer arrives incrementally, printed
live exactly like Lesson 5.

```python
messages.append({"role": "assistant", "content": content, "tool_calls": tool_calls})
```

Reconstructing the assistant message manually here (rather than
appending `response.message` directly, as Lesson 11 and 17 did)
because streaming never hands you one complete message object,
just chunks, so the loop builds the equivalent by hand from what it
collected.

## Running it

```bash
uv run python lessons/ollama/03_advanced/24_advanced_capstone_project/lesson.py
```

## Expected output

```
Checking Ollama is ready...
Building the notes index (splitting + embedding)...

Q1: What practice schedule am I following for cello?
  [tool] search_notes({'query': 'cello practice schedule'}) -> "Music practice log: currently learning Bach's Cello Suite No"
It seems like you're following a practice schedule of 30 minutes a day, 5 days a week, for the Prelude movement of Bach's Cello Suite No. 1. This schedule allows you to focus on a gradual increase in speed with a metronome, which can help you improve your technique and play with more accuracy and confidence. Is there anything specific you'd like to know or any adjustments you'd like to make to your practice schedule?

Q2: If I practice that many minutes a day, how many minutes total per week?
  [tool] calculate({'expression': '30*5'}) -> '150'
You will practice for a total of 150 minutes per week.
```

Exact wording of the two natural-language answers will vary between
runs, but Q2's final number should always be 150, real arithmetic on
the real number retrieved in Q1, proof the tool-calling loop and the
conversation memory are both genuinely working together, not just
producing plausible-sounding text.

## Course checkpoint

If this capstone ran cleanly and made sense without looking anything
up, you've built a real local agent from nothing but the `ollama`
package: chat, streaming, structured output, tool calling, memory,
custom models, and RAG, all without a single request leaving your own
machine. From here, Lessons 13-14 showed how the exact same local
model slots into LangChain or pydantic_ai if your agent needs their
broader ecosystem (LangGraph, MCP, evals); this capstone showed you
never strictly need to reach for them, the raw `ollama` package alone
is enough to build something real.
