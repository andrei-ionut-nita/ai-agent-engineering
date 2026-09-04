# Lesson 23: Wrapping It as a Service

## Where we left off

Lesson 22 drew the exact boundary a web service needs: `build_registry()`
does expensive, once-only setup, `answer()` does per-question work. This
lesson wires that boundary into an actual, if minimal, FastAPI app, the
same graduation every prior course's own Lesson 24 already made for its
own single-strategy `ingest()`/`ask()`, applied here to a whole registry
instead of one collection.

## The code, piece by piece

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.registry = build_registry()
    yield
```

`build_registry()` runs exactly once, when the app starts, ingesting
through all three wired strategies (naive, corrective, graph) and
storing the resulting registry on `app.state`, reachable from any
request handler.

```python
@app.get("/ask", response_model=AskResponse)
def ask_endpoint(q: str, k: int = 2) -> AskResponse:
    strategy_name, response_text = answer(q, app.state.registry, k)
    return AskResponse(answer=response_text, strategy=strategy_name)
```

One route, `GET /ask?q=...`, that does nothing but call `answer()`
(Lesson 22, unchanged) against the registry built at startup. The
response includes which strategy handled the question, not just the
answer text, since "which strategy, and why" is this whole course's
distinguishing feature over any single-strategy service from courses
1-5.

## Running it

```bash
uv run python lessons/adaptive_rag/03_advanced/23_wrapping_it_as_a_service/lesson.py
```

To run it as a real, live server instead:

```bash
cd lessons/adaptive_rag/03_advanced/23_wrapping_it_as_a_service
uvicorn lesson:app --reload
```

Then, in another terminal: `curl "http://127.0.0.1:8000/ask?q=What+oven+setting+does+the+pizza+dough+recipe+use%3F"`

## Expected output

```
GET /ask?q='What oven setting does the pizza dough recipe use?'
  {'answer': '<a grounded answer citing pizza-dough.md>', 'strategy': 'naive'}

GET /ask?q='How does wind speed affect things around the house?'
  {'answer': '<corrective_rag's real graded answer>', 'strategy': 'corrective'}
```

The classifier's exact label can vary run to run, so a specific question
routing to a different strategy than shown above isn't a bug, the same
honest variability Lesson 16 covers in more depth.

## Checkpoint

- `lifespan` is where `build_registry()` runs, once, the natural home
  for any "expensive setup" this series has built since Lesson 5.
- The response shape (`answer` plus `strategy`) is this course's own
  addition to every prior course's `{"answer": ...}` service response,
  disclosing the routing decision alongside the answer it produced.
- Everything inside `/ask` is Lesson 22's `answer()`, completely unaware
  it's being called from an HTTP route instead of a script's `main()`.

If anything here still feels unclear, ask before moving to Lesson 24.
