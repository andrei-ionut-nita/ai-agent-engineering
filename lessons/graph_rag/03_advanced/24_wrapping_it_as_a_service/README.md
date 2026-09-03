# Lesson 24: Wrapping It as a Service

## Where we left off

Lesson 23 split this course's pipeline into `ingest()` (run once) and
`ask()` (run per question), specifically so it matches how a real web
service works. This lesson wires those two functions into a FastAPI
app, the same pattern `naive_rag` Lesson 24 already covered in depth,
brief here on purpose: this course's own pedagogical weight belongs to
Lesson 16's error-compounding demonstration, not a second full FastAPI
walkthrough. If any of this lesson's mechanics (`lifespan`,
`app.state`, `TestClient`) feel unfamiliar, read `naive_rag` Lesson 24's
README first, it explains each one in full; this lesson only shows what
changed to fit this course's `State`.

## What actually changed from `naive_rag` Lesson 24

Almost nothing structurally. The one real difference: `app.state` now
holds this course's `State` NamedTuple (`graph` and `collection`)
instead of a bare `chromadb.Collection`, because this course's `ask()`
needs both pieces, not just one.

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    docs = sorted(NOTES_DIR.glob("*.md"))
    app.state.graph_state = ingest(docs)
    yield


@app.get("/ask", response_model=AskResponse)
def ask_endpoint(q: str, k: int = 2) -> AskResponse:
    return AskResponse(answer=ask(q, app.state.graph_state, k))
```

`ingest()` runs once at startup, same as `naive_rag` Lesson 24.
`ask_endpoint` calls Lesson 23's `ask()` unchanged. Everything else,
`lifespan`, `TestClient`, the single `/ask` route, is identical in
shape to `naive_rag` Lesson 24.

## Running it

```bash
uv run python lessons/graph_rag/03_advanced/24_wrapping_it_as_a_service/lesson.py
```

To run it as a real, live server instead:

```bash
cd lessons/graph_rag/03_advanced/24_wrapping_it_as_a_service
uvicorn lesson:app --reload
```

Then, in another terminal:
`curl "http://127.0.0.1:8000/ask?q=What%27s+stored+on+the+garage+electronics+bench%3F"`

## Expected output

```
GET /ask?q="What's stored on the garage electronics bench?"
  {'answer': 'Based on the provided facts, the garage electronics bench holds a soldering station, a parts bin, a Raspberry Pi, and a multimeter.'}

GET /ask?q='What is the capital of France?'
  {'answer': 'Based on the provided facts, there is no mention of France or its capital.'}
```

## Checkpoint

- This lesson is Lesson 23's `ingest()`/`ask()` wired to FastAPI's
  `lifespan` and one route, exactly `naive_rag` Lesson 24's pattern.
- The only real change from that lesson: `app.state` holds this
  course's two-field `State`, not a bare `Collection`, because this
  course's `ask()` needs the graph and the vector index both.
- Everything running inside `/ask` is Lesson 23's `ask()`, unaware it's
  being called from an HTTP route instead of a script's `main()`.

If anything here still feels unclear, read `naive_rag` Lesson 24's
README for the fuller walkthrough, then ask before moving to Lesson 25.
