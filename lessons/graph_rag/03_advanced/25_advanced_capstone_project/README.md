# Lesson 25: Advanced Capstone - A Complete Graph RAG Service

## What this is

No new concepts in this lesson. This is the course's capstone: a small,
real FastAPI service built entirely out of ideas from Lessons 1 through
24, combined into one thing. If you can read `lesson.py` and understand
why every piece is there, you've mastered this course. If any piece
feels unfamiliar, that's a sign to revisit the lesson it came from.

## What it does

Ingests every fixture note into a `networkx` graph plus a `chromadb`
node index at startup (Lesson 23's `ingest()`, unchanged), then serves
a `GET /ask` endpoint that finds a starting entity via `chromadb`,
traverses the graph to gather connected facts with provenance, cites
which source file each fact came from (Lesson 15), and admits when a
detail genuinely isn't supported, the same behavior as Lesson 18, now
reachable over HTTP.

## Where each piece came from

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    docs = sorted(NOTES_DIR.glob("*.md"))
    app.state.graph_state = ingest(docs)
```
Lesson 24 (the service shell) plus Lesson 23's `ingest()`, run once at
startup, building both halves of `State`.

```python
def ingest(docs: list[Path]) -> State:
    graph = nx.DiGraph()
    provenance: Provenance = {}
    for path in docs:
        for subject, relation, obj in extract_relationships(path.read_text()):
            graph.add_edge(subject, obj, relation=relation)
            provenance.setdefault(subject, set()).add(path.name)
            provenance.setdefault(obj, set()).add(path.name)
    ...
    return State(graph=graph, collection=collection, provenance=provenance)
```
Lesson 23's `ingest()`, extended with Lesson 12's provenance tracking,
the one addition this capstone needed: `State` grows a third field so
`ask()` can cite its sources.

```python
start = find_starting_node(query, state.collection)
facts = gather_facts_with_sources(state.graph, state.provenance, start, max_hops=3)
```
Lesson 22 (`chromadb`-backed starting-node lookup) feeding into Lesson
15's provenance-aware traversal, now running on `networkx` (Lesson 21)
instead of the hand-rolled dict.

```python
if not facts:
    return "I don't have any information relevant to that question."
```
Lesson 15 (skip the generation call when traversal found nothing to
work with).

```python
prompt = f"""...after each claim, cite the source file in square brackets..."""
```
Lesson 15's grounded, citation-requiring prompt, unchanged.

## Running it

```bash
uv run python lessons/graph_rag/03_advanced/25_advanced_capstone_project/lesson.py
```

To run it as a real, live server: `uvicorn lesson:app --reload` from
this folder, then `curl "http://127.0.0.1:8000/ask?q=..."`.

## Expected output

```
GET /ask?q="Who recalibrated the sensor that Dev flagged as drifting in the greenhouse, and what tool did they use?"
  {'answer': 'Mia recalibrated the humidity sensor that Dev flagged [greenhouse.md, maintenance-log.md]...'}

GET /ask?q='What is the capital of France?'
  {'answer': "I don't have any information relevant to that question."}
```

## Documented limitations

This capstone is a complete, working Graph RAG service, and it's still
worth being explicit about what it doesn't handle, the same honesty
`naive_rag` Lesson 26 modeled for that course:

- **Extraction errors compound silently** (Lesson 16). This service has
  no way to detect a wrong or missing triple on its own; a bad
  extraction degrades an answer without raising an error anywhere.
- **Traversal depth is fixed, not adaptive** (Lesson 14). Every question
  traverses the same number of hops, regardless of whether the answer
  actually needs one hop or four.
- **Entity normalization (Lesson 11) runs once, at ingest time.** A new
  document added later that introduces yet another name for an
  already-known entity won't get merged in until the whole graph is
  rebuilt from scratch.
- **No retrieval quality check before generation.** Unlike `naive_rag`
  Lesson 25's `MIN_SCORE` floor, this service never verifies the
  starting node `chromadb` picked was actually a good match, a
  sufficiently strange question can traverse from a wrong starting
  point with no warning.

That last point in particular, retrieving without ever checking whether
what was retrieved is any good, is exactly where this series' next
course picks up.

## Try this yourself

Without looking anything up:

- Add a new fixture `.md` file and confirm a question about it gets
  ingested, traversed, and cited correctly without any other code
  change.
- Run `uvicorn lesson:app --reload` from this folder and hit `GET
  /ask?q=...` from a browser or `curl`, confirm it behaves identically
  to the `TestClient` calls in the script.
- Ask a question this service clearly can't answer well (something
  needing five hops), and read its answer critically: does it hedge
  honestly, or does it confidently answer using only part of the real
  picture?

This is where Graph RAG, built entirely from scratch, ends up: a small,
real, citation-aware, multi-hop-answering service. Lesson 26 is a
short, code-free look at where this specific architecture still falls
short, and which course in this series picks up each of those threads.
