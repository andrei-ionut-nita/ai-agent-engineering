# Lesson 24: Wrapping It as a Service

## Where we left off

This is a short recipe lesson, not a new-concepts lesson. `naive_rag`
Lesson 24 already taught FastAPI's `lifespan` hook, `app.state`, and
`TestClient`, in depth, this lesson reuses that exact pattern almost
verbatim, the only thing that changed is which `ingest()`/`ask()` pair
gets wired in. If any of `lifespan`, `app.state`, or `TestClient` feel
unfamiliar, go read `naive_rag` Lesson 24's README first, this one
won't re-teach them.

## What actually changed from naive_rag Lesson 24

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.corrective_state = ingest(NOTES_DIR)
    yield
```

One line: `ingest()` now returns Lesson 23's `CorrectiveState`
(collection + grader) instead of a bare `chromadb.Collection`, and it's
stored on `app.state.corrective_state` instead of `app.state.collection`.
Everything else about the lifespan hook is identical.

```python
@app.get("/ask", response_model=AskResponse)
def ask_endpoint(q: str, k: int = 2) -> AskResponse:
    return AskResponse(answer=ask(q, app.state.corrective_state, k))
```

Also identical in shape to `naive_rag` Lesson 24's one route, `ask()`
itself does more work now (grading, filtering, rewriting), but the
route calling it doesn't need to know that, it's still one function
call.

## Running it

```bash
uv run python lessons/corrective_rag/03_advanced/24_wrapping_it_as_a_service/lesson.py
```

Or as a real, live server:

```bash
cd lessons/corrective_rag/03_advanced/24_wrapping_it_as_a_service
uvicorn lesson:app --reload
```

Then, in another terminal:
`curl "http://127.0.0.1:8000/ask?q=What%20is%20the%20capital%20of%20France%3F"`

## Expected output

```
GET /ask?q="Project Aurora's Raspberry Pi writes sensor readings to a SQLite file on its SD card. Where does that Raspberry Pi physically live in the house?"
  {'answer': "Based on the context provided, Project Aurora's Raspberry Pi physically lives on a small shelf next to the bookshelf in the study."}

GET /ask?q='What is the capital of France?'
  {'answer': "I don't have any information relevant to that question."}
```

## Checkpoint

- This lesson intentionally doesn't re-teach FastAPI, see `naive_rag`
  Lesson 24 for that depth.
- The only real change: `app.state` now holds a `CorrectiveState`
  (Lesson 23), not a bare collection, and `ask()` internally grades and
  corrects before generating, invisibly to the route handler.
- Lesson 16's grader-circularity demo, not this lesson, is where this
  course's real depth lives, this lesson exists to show the pipeline is
  service-shaped, nothing more.

If anything here still feels unclear, ask before moving to Lesson 25.
