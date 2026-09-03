# Lesson 25: Advanced Capstone - A Complete Multimodal RAG Service

## What this is

No new concepts in this lesson. This is the course's capstone: a small,
real FastAPI service built entirely out of ideas from Lessons 1 through
24, combined into one thing. If you can read `lesson.py` and understand
why every piece is there, you've mastered this course. If any piece
feels unfamiliar, that's a sign to revisit the lesson it came from.

## What it does

Ingests all five fixture notes and all five image sources (four
standalone figures plus the one embedded in
`circuit-board-notebook.pdf`) into a chromadb collection at startup,
ten records total, each carrying `modality`, `source`, and
`image_path`/`image_bytes` metadata. Serves `GET /ask`, which retrieves
across both modalities, re-attaches the original image at generation
time whenever the best match is one, cites whether each fact came from
a text note or an image, and returns the original image's filename
alongside the answer when relevant. Serves `GET /image/{filename}` to
fetch that file directly.

## Where each piece came from

```python
def extract_images_from_pdf(pdf_path: Path) -> list[bytes]:
```
Lesson 17: the one image source in this fixture set that isn't a
standalone `.png`.

```python
metadatas = [{"modality": ..., "source": ..., "image_path": ...}, ...]
```
Lesson 22's `State` shape, unchanged: one chromadb collection, both
modalities, `image_path` an empty string for text records.

```python
if metadata["image_path"]:
    image_bytes = Path(metadata["image_path"]).read_bytes()
    parts.append(types.Part.from_bytes(...))
```
Lesson 8 (re-attach the original image at generation time) plus Lesson
14 (modality-labeled citation prompt), running against chromadb
metadata instead of a Python dict's `image_path is not None` field.

```python
@app.get("/image/{filename}")
def get_image(filename: str) -> FileResponse:
```
Lesson 24, unchanged: serve the actual retrieved image back to the
caller, not just a description of it.

## Running it

```bash
uv run python lessons/multimodal_rag/03_advanced/25_advanced_capstone_project/lesson.py
```

To run it as a real, live server: `uvicorn lesson:app --reload` from
this folder, then `curl "http://127.0.0.1:8000/ask?q=..."`.

## Expected output

```
GET /ask?q="What frequency was measured on the 555 timer's pin 3 output?"
  {'answer': '<a grounded answer mentioning 2 Hz, citing the notebook PDF image>', 'source_image': None}

GET /ask?q="What's the torque spec for the derailleur hanger bolt?"
  {'answer': '<a grounded answer mentioning 8 Nm>', 'source_image': 'derailleur-hanger-diagram.png'}

GET /ask?q='What is the capital of France?'
  {'answer': "I don't have any information relevant to that question.", 'source_image': None}
```

(The PDF-sourced record's `source_image` stays `None` here, its bytes
were extracted from a PDF page rather than read from a standalone
`.png` file, so there's no single filename `/image/{filename}` could
serve; extending that route to also serve PDF-extracted images is one
of this lesson's "try this yourself" prompts.)

## Try this yourself

Without looking anything up:

- Add a new fixture note with no image at all, confirm ingestion and
  retrieval both work unmodified, on purpose, not every document needs
  every modality.
- Extend `get_image` (or add a new route) to serve the PDF-extracted
  image back to a caller too, given the bytes are already extracted at
  ingest time, where would you cache them so a request doesn't need to
  re-parse the PDF every time?
- Run `uvicorn lesson:app --reload` from this folder and hit `GET
  /ask?q=...` from a browser or `curl`, confirm it behaves identically
  to the `TestClient` calls in the script.

This is where Multimodal RAG, built by extending `naive_rag`'s exact
pipeline with one new idea (captioning-then-embed), ends up: a small,
real, citation-aware, cross-modal service. Lesson 26 is a short,
code-free look at where this specific architecture still falls short.
