# Lesson 24: Serving the Original Image Back to the Caller

## Where we left off

Lesson 23's service re-attaches a retrieved image to *Gemini* (Lesson
8's idea, unchanged) but only ever returns text to the *caller*. A real
caller (a UI showing search results, say) often wants the actual image
back too, not just a paragraph describing it, especially when the best
match is a diagram someone would rather look at directly than read a
description of. This lesson adds that: when the top retrieved record is
an image, the response includes enough for the caller to fetch the
original file themselves.

## The code, piece by piece

```python
class AskResponse(BaseModel):
    answer: str
    source_image: str | None = None
```

One new, optional field. `None` when the retrieved context was text
only; the image's filename when the best-scoring retrieved record was
an image, letting a caller distinguish "here's a written answer" from
"here's a written answer, and here's the image it came from, look at it
yourself."

```python
@app.get("/image/{filename}")
def get_image(filename: str) -> FileResponse:
    image_path = IMAGES_DIR / filename
    if not image_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path, media_type="image/png")
```

A second route, deliberately simple: given a filename (from
`source_image` in a prior `/ask` response), serve the actual file bytes
back over HTTP. `FileResponse` streams the file directly, no manual
byte-reading required, this is the standard FastAPI way to serve a
static file from a route. Path validation (`is_file()`, a 404 otherwise)
matters here specifically because `filename` comes from a caller,
serving an arbitrary path from user input without checking it first
would let a request read any file the process can access.

```python
top_metadata = retrieved_metadatas[0]
source_image = top_metadata["source"] if top_metadata["modality"] == "image" else None
```

Whether to set `source_image` is decided from the *top* retrieved
record only, matching the intuition "the single best match is what the
caller most likely wants to see", not every image that happened to be
in the retrieved set.

## Running it

```bash
uv run python lessons/multimodal_rag/03_advanced/24_serving_the_original_image_back/lesson.py
```

To run it as a real, live server: `uvicorn lesson:app --reload` from
this folder, then:

```bash
curl "http://127.0.0.1:8000/ask?q=What%27s+the+torque+spec%3F"
curl "http://127.0.0.1:8000/image/derailleur-hanger-diagram.png" --output diagram.png
```

## Expected output

```
GET /ask?q="What's the torque spec for the derailleur hanger bolt?"
  {'answer': '<a grounded answer mentioning 8 Nm>', 'source_image': 'derailleur-hanger-diagram.png'}

GET /ask?q='What is the capital of France?'
  {'answer': '<an honest admission the retrieved context doesn't answer this>', 'source_image': None}

GET /image/derailleur-hanger-diagram.png -> 200, image/png, <N> bytes
```

## Checkpoint

- Answering *about* an image (Lesson 8, Gemini re-reading it) and
  serving the image *back to the caller* are two different things; a
  real service usually needs both.
- `FileResponse` is FastAPI's standard tool for streaming a file back
  over HTTP; validate any caller-supplied path before touching the
  filesystem with it.
- `source_image` is set from the top retrieved record only, a
  deliberate, simple choice, not every retrieved image.

If anything here still feels unclear, ask before moving to Lesson 25.
