# Lesson 23: Wrapping It as a Service

## Where we left off

This is a short recipe, not a new concept: `naive_rag` Lesson 24
already taught what `lifespan`, `app.state`, and `TestClient` do and
why a FastAPI wrapper is structured this way. Nothing about that
changes here, `ingest()` and `ask()` (Lesson 22) slot into the exact
same shell unmodified. This lesson exists so the course has a complete,
runnable service, not to re-teach FastAPI, Lessons 7-8 (cross-modal
retrieval and re-attaching the original image) carry this course's real
depth.

## The code, piece by piece

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    chroma_client = chromadb.Client()
    app.state.collection = ingest(NOTES_DIR, IMAGES_DIR, chroma_client)
    yield


@app.get("/ask", response_model=AskResponse)
def ask_endpoint(q: str, k: int = 2) -> AskResponse:
    return AskResponse(answer=ask(q, app.state.collection, k))
```

`naive_rag` Lesson 24's exact shape, `ingest()` now takes two directory
arguments (`notes_dir`, `images_dir`) instead of one, everything else,
`lifespan` running once at startup, one `GET /ask` route, `TestClient`
running the app in-process, is unchanged.

## Running it

```bash
uv run python lessons/multimodal_rag/03_advanced/23_wrapping_it_as_a_service/lesson.py
```

To run it as a real, live server:

```bash
cd lessons/multimodal_rag/03_advanced/23_wrapping_it_as_a_service
uvicorn lesson:app --reload
```

Then, in another terminal: `curl "http://127.0.0.1:8000/ask?q=What%27s+the+torque+spec+for+the+derailleur+hanger+bolt%3F"`

## Expected output

```
GET /ask?q="What's the torque spec for the derailleur hanger bolt?"
  {'answer': '<a grounded answer citing the image, mentioning 8 Nm>'}
```

## Checkpoint

- If `lifespan`, `app.state`, or `TestClient` feel unfamiliar, go back
  to `naive_rag` Lesson 24, this lesson deliberately doesn't re-explain
  them.
- The only thing specific to this course is that `ingest()` now builds
  a mixed-modality collection; the service shell around it is
  identical to every other course in this series that has one.

If anything here still feels unclear, ask before moving to Lesson 24.
