# Lesson 25: Advanced Capstone - A Complete Agentic RAG Service

## What this is

No new concepts in this lesson. This is the course's capstone: a small,
real FastAPI service built entirely out of ideas from Lessons 1 through
24, combined into one thing. If you can read `lesson.py` and understand
why every piece is there, you've mastered this course. If any piece
feels unfamiliar, that's a sign to revisit the lesson it came from.

## What it does

Ingests every fixture note into a chromadb collection at startup, then
serves a `GET /ask` endpoint backed by a four-tool agent
(`search_notes`, `get_current_datetime`, `calculate`, `grade_passage`)
that decides, per question, what to call, how many times, and cites its
sources when it does retrieve, reachable over HTTP, all four tools
available, no code path hardcoded to any one of them.

## Where each piece came from

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    chroma_client = chromadb.Client()
    app.state.agent_state = ingest(NOTES_DIR, chroma_client)
```
Lesson 24 (the service shell) plus Lesson 23 (`ingest()`, run once at
startup, returning `State`).

```python
def tools(collection: chromadb.Collection) -> ToolRegistry:
    return {"search_notes": Tool(...), "get_current_datetime": Tool(...), "calculate": Tool(...), "grade_passage": Tool(...)}
```
Lesson 21's registry pattern, Lesson 22's optional fourth tool
included this time, all four bundled the same way, one dict entry
each.

```python
def run_agent(query: str, registry: ToolRegistry, max_steps: int = MAX_STEPS) -> str:
    ...
    result = {"output": tool.fn(**(call.args or {}))} except -> {"error": ...}
```
Lesson 16's error-safe dispatch (any tool exception becomes an
`{"error": ...}` function response) and Lesson 14's `MAX_STEPS` bound,
both unconditional, every call goes through both protections.

```python
SYSTEM_INSTRUCTION = """... Only call search_notes for questions about
the personal topics it covers ... call search_notes once per part ...
call grade_passage to check ... cite the source file ..."""
```
Lesson 6's "don't retrieve unnecessarily" steering, Lesson 11's
decomposition instruction, Lesson 22's optional grading, and Lesson
15's citation requirement, combined into one standing instruction for
the whole service.

```python
def ask(query: str, state: State, k: int = 1) -> str:
    _, registry = state
    return run_agent(query, registry)
```
Lesson 23's Strategy-protocol boundary, unchanged, this is the only
function `ask_endpoint()` calls.

## Running it

```bash
uv run python lessons/agentic_rag/03_advanced/25_advanced_capstone_project/lesson.py
```

To run it as a real, live server: `uvicorn lesson:app --reload` from
this folder, then `curl "http://127.0.0.1:8000/ask?q=..."`.

## Expected output

```
GET /ask?q='How often does the sourdough starter need feeding at room temperature?'
  {'answer': 'The sourdough starter needs feeding every 12 hours at room temperature [sourdough-starter.md].'}

GET /ask?q='What time is it right now in Lisbon?'
  {'answer': '<the current date and time in Europe/Lisbon>'}

GET /ask?q='What is 8 times 7?'
  {'answer': '56'}

GET /ask?q='How is the vinyl collection organized, and how far along is the Japanese study journal toward JLPT N3?'
  {'answer': '<a combined, dual-cited answer covering both parts>'}

GET /ask?q='What is the chemical symbol for gold?'
  {'answer': 'Au'}
```

## Try this yourself

Without looking anything up:

- Add a fifth tool of your own (a unit converter, a word counter,
  anything trivial) via `tools()`, confirm it works with a targeted
  question, and count how many lines you had to change outside
  `tools()` itself.
- Remove `grade_passage` from `SYSTEM_INSTRUCTION`'s mention entirely
  (leave the tool registered) and ask a deliberately ambiguous
  question. Does the agent still reach for it on its own, or does it
  need the instruction to know when it's appropriate?
- Run `uvicorn lesson:app --reload` from this folder and hit `GET
  /ask?q=...` from a browser or `curl`, confirm it behaves identically
  to the `TestClient` calls in the script.

This is where Agentic RAG, built entirely from scratch, ends up: a
small, real, multi-tool service that decides for itself what to do with
each question. Lesson 26 is a short, code-free look at where this
specific architecture still falls short, and which course in this
series picks up each of those threads.
