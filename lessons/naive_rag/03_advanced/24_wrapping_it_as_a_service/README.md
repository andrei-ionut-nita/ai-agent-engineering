# Lesson 24: Wrapping It as a Service

## Where we left off

Lesson 23 split this course's pipeline into `ingest()` (run once) and
`ask()` (run per question), specifically because that boundary matches
how a real web service works: build the index at startup, answer
requests as they arrive. This lesson wires those two functions into an
actual, if minimal, FastAPI app.

## The code, piece by piece

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    chroma_client = chromadb.Client()
    app.state.collection = ingest(NOTES_DIR, chroma_client)
    yield
```

FastAPI's `lifespan` runs once, when the app starts (and again, after
`yield`, when it shuts down, unused here). `ingest()` runs exactly here,
producing a `collection` stored on `app.state`, a place any request
handler can reach it from. This is the "expensive setup happens once"
half of Lesson 23's whole point, now literally wired to the server's own
startup event instead of the top of a script.

```python
@app.get("/ask", response_model=AskResponse)
def ask_endpoint(q: str, k: int = 2) -> AskResponse:
    return AskResponse(answer=ask(q, app.state.collection, k))
```

One route, `GET /ask?q=...`, that does nothing but call `ask()` (Lesson
23, unchanged) against the collection built at startup. This is the
entire service: `ingest()` once, `ask()` per request, exactly the
division Lesson 23 drew.

```python
with TestClient(app) as test_client:
    response = test_client.get("/ask", params={"q": question})
```

`TestClient` runs the FastAPI app in-process, no real network socket
involved, so `uv run python lesson.py` can exercise the API the same way
every other lesson's `main()` runs and prints something, without needing
a second terminal running a live server.

## Running it

```bash
uv run python lessons/naive_rag/03_advanced/24_wrapping_it_as_a_service/lesson.py
```

To run it as a real, live server instead (useful for hitting it from a
browser or `curl`):

```bash
cd lessons/naive_rag/03_advanced/24_wrapping_it_as_a_service
uvicorn lesson:app --reload
```

Then, in another terminal: `curl "http://127.0.0.1:8000/ask?q=What%27s+the+best+way+to+get+a+crispy+pizza+crust%3F"`

## Expected output

```
GET /ask?q="What's the best way to get a crispy pizza crust?"
  {'answer': '<a grounded answer about 00 flour, cold ferment, preheated steel>'}

GET /ask?q='What is the capital of France?'
  {'answer': "I don't have any information relevant to that question."}
```

## Checkpoint

- **`lifespan`**: FastAPI's hook for code that runs once at startup
  (and once at shutdown), the natural home for `ingest()`.
- **`app.state`**: where a value built at startup (the `collection`)
  gets stored so request handlers can reach it later.
- **`TestClient`**: exercises a FastAPI app in-process, no live server
  needed, useful for running a service lesson the same way every other
  lesson runs, with `uv run python lesson.py`.
- Everything running inside `/ask` is Lesson 23's `ask()`, completely
  unaware it's being called from an HTTP route instead of a script's
  `main()`.

If anything here still feels unclear, ask before moving to Lesson 25.
