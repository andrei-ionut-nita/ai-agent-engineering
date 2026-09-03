# Lesson 4: Captioning an Image

## Where we left off

Lesson 3 proved Gemini can answer a direct question about one image
handed to it in the same call. That's not retrieval, a real system
doesn't know in advance which image (if any) a future question will
need, so it can't attach every image to every query. What it *can* do
ahead of time is describe every image once, in detail, as text, and
make that description retrievable the same way this series has made
text chunks retrievable since `naive_rag` Lesson 2. This lesson writes
that description step: **captioning**.

## What makes a caption "retrievable detail"

A generic caption like "a diagram of a mechanical part" would embed to
something semantically close to *every* mechanical diagram in a
corpus, useless for telling this image apart from another one. A
caption written to be retrieved needs the *specific* details a real
question might ask for: numbers, labels, colors, positions, anything
printed or drawn in the image, not just its general subject. That's
the instruction `CAPTION_PROMPT` gives Gemini below, and it's the same
principle Lesson 15 (later) revisits as a caption's failure mode: a
caption that drops a specific detail makes that detail permanently
unretrievable, no matter how good retrieval's embedding or ranking is.

## The code, piece by piece

```python
CAPTION_PROMPT = (
    "Describe this image in detail, for someone who cannot see it. "
    "Include any text, numbers, labels, or colors visible in the image, "
    "exactly as shown. Be specific and factual, do not guess at anything "
    "not visible."
)
```

Three things this prompt does on purpose: asks for specificity ("any
text, numbers, labels, or colors"), asks the model to transcribe visible
text exactly rather than paraphrase it (a torque spec of "8 Nm" needs to
stay "8 Nm" in the caption, not become "a small number"), and explicitly
forbids guessing, the same "don't invent what isn't there" instruction
Lesson 15 (of `naive_rag`) used for grounded text answers, now applied
to image description instead.

```python
def caption_image(image_path: Path) -> str:
    image_bytes = image_path.read_bytes()
    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=[image_part, CAPTION_PROMPT],
    )
    return response.text or ""
```

Exactly Lesson 3's call, generalized into a function and with the
one-off `QUESTION` replaced by `CAPTION_PROMPT`. This function is the
one new building block this course adds to `naive_rag`'s pipeline;
every later lesson that touches an image calls this, unchanged.

## Running it

```bash
uv run python lessons/multimodal_rag/01_beginner/04_captioning_an_image/lesson.py
```

## Expected output

```
Captioning derailleur-hanger-diagram.png...

Caption:
<a detailed description mentioning "8 Nm" and "red", wording varies>
```

## Checkpoint

- **Captioning**: describing an image in detailed text, so it can later
  be embedded and retrieved the same way a text chunk is, without
  retrieval ever touching pixels directly.
- A caption is only as useful as it is *specific*: numbers, labels, and
  colors preserved exactly, not paraphrased away.
- `caption_image()` is this course's one new function; everything after
  captioning reuses `naive_rag`'s pipeline unchanged, on the caption's
  text instead of a document's text.

## Try this yourself

Without looking anything up:

- Caption `observatory-finder-scope.png` instead, does the caption
  preserve "3 mm left, 2 mm up" exactly, or does it round or paraphrase
  the numbers?
- Remove the "do not guess at anything not visible" sentence from
  `CAPTION_PROMPT` and re-run against the same image. Does the caption
  change in a way you can point to?

If anything here still feels unclear, ask before moving to Lesson 5.
