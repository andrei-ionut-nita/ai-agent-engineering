# Lesson 3: Sending an Image to Gemini

## Where we left off

Lesson 2 established the problem: some facts only exist in an image.
This lesson is the smallest possible step toward fixing it, sending
Gemini one image, alongside a text prompt, in a single `generate_content`
call. No embedding, no retrieval yet, just: can Gemini look at a picture
and answer a question about it?

## The code, piece by piece

```python
from google.genai import types

image_bytes = image_path.read_bytes()
image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
```

`generate_content`'s `contents` argument isn't limited to a string, it
accepts a list of `Part` objects, and `Part` isn't limited to text
either (confirmed against this project's installed `google-genai`
version, `google/genai/types.py`). `Part.from_bytes` wraps raw image
bytes and a MIME type into the same kind of object a text prompt
becomes internally; Gemini's models are natively multimodal, so mixing
an image `Part` and a text `Part` in one `contents` list is not a
special mode, it's the normal way to send more than plain text.

```python
response = client.models.generate_content(
    model=CHAT_MODEL,
    contents=[image_part, QUESTION],
)
```

A bare string in `contents` (like `QUESTION` here) is automatically
wrapped into a text `Part` for you, the SDK doesn't require you to
write `types.Part.from_text(text=...)` yourself for something this
simple. Order in the list matters for how the model reads the prompt,
not for correctness, image-then-question and question-then-image both
work; this course puts the image first throughout, so the question that
follows always reads like "given this, answer: ...".

## Running it

```bash
uv run python lessons/multimodal_rag/01_beginner/03_sending_an_image_to_gemini/lesson.py
```

## Expected output

```
Image: derailleur-hanger-diagram.png
Question: What's the torque spec printed on this part, and what color is it printed in?

Gemini's answer:
<a correct answer describing "8 Nm" printed in red, wording varies>
```

Compare this to Lesson 1's answer to nearly the same question with no
image attached at all, the only thing that changed is one `Part` in the
`contents` list.

## Checkpoint

- **`types.Part.from_bytes(data=..., mime_type=...)`**: wraps raw image
  bytes into the same kind of object Gemini's SDK uses for text.
- **`contents=[image_part, "some text"]`**: mixing an image `Part` and
  a plain string in one list is the normal way to send a multimodal
  prompt, the string is auto-wrapped as text.
- This alone does not make images retrievable, it only proves Gemini
  can *read* one when it's handed directly. Lesson 4 turns that reading
  into text worth storing.

If anything here still feels unclear, ask before moving to Lesson 4.
