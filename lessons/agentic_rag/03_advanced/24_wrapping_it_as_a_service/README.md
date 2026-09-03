# Lesson 24: Wrapping It as a Service

## Where we left off

This is a short recipe, not a new concept. [naive_rag Lesson 24](../../../naive_rag/03_advanced/24_wrapping_it_as_a_service/README.md)
already taught the whole idea, `ingest()` runs once at startup via
FastAPI's `lifespan`, `ask()` runs per request. Lesson 23 built this
course's own `ingest()`/`ask()` pair; this lesson just wires them into
the identical FastAPI shape, worth doing because the loop underneath
(function calling, multi-step tool dispatch) is meaningfully more
complex than a plain retrieve-and-generate pipeline, and it's worth
confirming that complexity disappears completely once it's behind
`ask()`.

## The code, piece by piece

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    chroma_client = chromadb.Client()
    app.state.agent_state = ingest(NOTES_DIR, chroma_client)
    yield
```

Identical structure to `naive_rag`'s version, `app.state.agent_state`
here instead of `app.state.collection`, holding this course's full
`State` (collection and tool registry both) instead of just a
collection.

```python
@app.get("/ask", response_model=AskResponse)
def ask_endpoint(q: str) -> AskResponse:
    return AskResponse(answer=ask(q, app.state.agent_state))
```

One route, exactly `naive_rag`'s shape. Everything about function
calling, multi-step loops, the tool registry, is fully contained inside
`ask()`, this handler has no idea any of it exists, which is precisely
the point of drawing the `ingest()`/`ask()` boundary in Lesson 23.

## Running it

```bash
uv run python lessons/agentic_rag/03_advanced/24_wrapping_it_as_a_service/lesson.py
```

To run it as a real, live server instead:

```bash
cd lessons/agentic_rag/03_advanced/24_wrapping_it_as_a_service
uvicorn lesson:app --reload
```

Then, in another terminal: `curl "http://127.0.0.1:8000/ask?q=What%27s+9+times+9%3F"`

## Expected output

```
GET /ask?q="How often does the sourdough starter need feeding at room temperature?"
  {'answer': 'The sourdough starter needs feeding every 12 hours at room temperature.'}

GET /ask?q="What's 9 times 9?"
  {'answer': '81'}
```

## Checkpoint

- Same `lifespan`/`app.state`/`TestClient` shape as
  `naive_rag` Lesson 24, applied to this course's `State` (a
  `chromadb.Collection` plus a tool registry) instead of just a
  collection.
- A route handler this simple is only possible because Lesson 23 drew
  a clean `ask(query, state, k) -> str` boundary around everything this
  course built since Lesson 3.

If anything here still feels unclear, ask before moving to Lesson 25.
