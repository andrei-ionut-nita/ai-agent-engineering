# Lesson 25: Advanced Capstone - A Complete Naive RAG Service

## What this is

No new concepts in this lesson. This is the course's capstone: a small,
real FastAPI service built entirely out of ideas from Lessons 1 through
24, combined into one thing. If you can read `lesson.py` and understand
why every piece is there, you've mastered this course. If any piece
feels unfamiliar, that's a sign to revisit the lesson it came from.

## What it does

Ingests every fixture note into a chromadb collection at startup, then
serves a `GET /ask` endpoint that retrieves relevant chunks (dropping
anything under a similarity threshold), cites its sources, and admits
when it doesn't know something, the same behavior as Lesson 15/18, now
running on chromadb instead of a Python list, and reachable over HTTP.

## Where each piece came from

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    chroma_client = chromadb.Client()
    app.state.collection = ingest(NOTES_DIR, chroma_client)
```
Lesson 24 (the service shell) plus Lesson 23 (`ingest()`, run once at
startup).

```python
results = collection.query(
    query_embeddings=[query_vector],
    n_results=k,
    include=["documents", "distances", "metadatas"],
)
```
Lesson 21 (chromadb-backed retrieval), extended to also request
`distances` and `metadatas`, both needed below.

```python
relevant = [
    (doc, meta["source"])
    for doc, distance, meta in zip(documents[0], distances[0], metadatas[0])
    if (1 - distance) >= MIN_SCORE
]
```
Lesson 14's threshold (`MIN_SCORE`), reimplemented against chromadb's
distance instead of this course's own cosine similarity. Since
chromadb's distance is smaller-is-more-similar (Lesson 20) and this
course's threshold was always phrased as similarity, `1 - distance`
converts back to the same direction before comparing.

```python
if not relevant:
    return "I don't have any information relevant to that question."
```
Lesson 15 (skip the API call when nothing clears the bar).

```python
context = "\n\n".join(f"[Source: {source}]\n{doc}" for doc, source in relevant)
```
Lesson 15/22 (metadata carried alongside each chunk, here `source` from
chromadb's own `metadatas` instead of a Python dict field).

```python
Rules:
- If the context doesn't contain the answer, say "I don't have information about that."
- Every claim in your answer must cite which source it came from...
```
Lesson 15's grounded, citation-requiring prompt, unchanged.

## Running it

```bash
uv run python lessons/naive_rag/03_advanced/25_advanced_capstone_project/lesson.py
```

To run it as a real, live server: `uvicorn lesson:app --reload` from
this folder, then `curl "http://127.0.0.1:8000/ask?q=..."`.

## Expected output

```
GET /ask?q="What's the cold ferment time for the pizza dough?"
  {'answer': 'The pizza dough uses a 48-hour cold ferment in the refrigerator (according to pizza-dough.md).'}

GET /ask?q='What is the capital of France?'
  {'answer': "I don't have any information relevant to that question."}
```

## Try this yourself

Without looking anything up:

- Lower `MIN_SCORE` and confirm the France question starts returning an
  (incorrect) attempt at an answer instead of the fallback message.
- Add a new fixture `.md` file and confirm a question about it gets
  ingested, retrieved, and cited correctly without any other code
  change.
- Run `uvicorn lesson:app --reload` from this folder and hit `GET
  /ask?q=...` from a browser or `curl`, confirm it behaves identically
  to the `TestClient` calls in the script.

This is where Naive RAG, built entirely from scratch, ends up: a small,
real, citation-aware service. Lesson 26 is a short, code-free look at
where this specific architecture still falls short, and which course in
this series picks up each of those threads.
