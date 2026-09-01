# Lesson 24: Wrapping It as a Service

## Where we left off

Same wiring as `naive_rag` Lesson 24, applied to this course's hybrid
`ingest()`/`ask()` from Lesson 23 instead of a dense-only pair. If you've
done that lesson, nothing here is new: `lifespan` builds the index once
at startup, `app.state` holds it for every request, one `GET /ask` route
calls `ask()` unchanged. This lesson is deliberately a short recipe, not
a re-teach, the plumbing is identical to `naive_rag` Lesson 24, only
`ingest()`/`ask()`'s internals (hybrid instead of dense-only) differ.

## The one real difference

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.hybrid = ingest(NOTES_DIR)
    yield
```

`app.state.hybrid` holds a `HybridState` (Lesson 23), both indexes,
instead of a single `chromadb.Collection`. Everything downstream, the
route handler, `ask()` itself, is otherwise the same shape as
`naive_rag`'s service.

## Running it

```bash
uv run python lessons/hybrid_rag/03_advanced/24_wrapping_it_as_a_service/lesson.py
```

Or as a real server: `cd` into this folder and run `uvicorn lesson:app --reload`, then `curl "http://127.0.0.1:8000/ask?q=20240115"`.

## Expected output

```
GET /ask?q='20240115'
  {'answer': "Based on the provided context, **20240115** is the router's firmware build that shipped the fix..."}

GET /ask?q='What is the capital of France?'
  {'answer': "The context doesn't contain the answer, so I cannot say."}
```

## Checkpoint

- Same `lifespan`/`app.state`/`TestClient` pattern as `naive_rag` Lesson
  24, wrapping a hybrid `ask()` instead of a dense-only one.
- The route handler never needed to know retrieval underneath is hybrid,
  it just calls `ask()`, exactly the payoff Lesson 23's function boundary
  was built for.

If anything here still feels unclear, ask before moving to Lesson 25.
