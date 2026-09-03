# Lesson 17: Extracting Images Embedded in a PDF Page

## Where we left off

Every image so far arrived as its own standalone `.png` file. Real
documents rarely cooperate: a scanned notebook page, a slide deck
exported to PDF, a report with inline figures, all deliver images
*embedded inside* a PDF page, not as separate files sitting in a
folder. This lesson handles that case using `circuit-board-notebook.pdf`,
a one-page PDF fixture whose single page has one embedded image (see
`fixtures/README.md`), extracting that image before handing it to
`caption_image()` exactly as if it had been a standalone file all
along.

## The code, piece by piece

```python
from pypdf import PdfReader

reader = PdfReader(PDF_PATH)
page = reader.pages[0]
for image_file in page.images:
    image_bytes = image_file.data
```

`pypdf` (already installed transitively in this project, via
`markitdown`/`docling`'s own dependencies) exposes each page's embedded
images through `page.images`, an iterable of `ImageFile` objects.
`.data` is the raw image bytes, exactly the same shape
`caption_image()` has expected since Lesson 4, whether those bytes
originally came from reading a `.png` file directly or from unpacking
them out of a PDF page changes nothing downstream.

```python
caption = caption_image_from_bytes(image_bytes, mime_type="image/jpeg")
```

One small change from `caption_image()`: the function now takes raw
bytes and a MIME type directly instead of a `Path` to read, since
there's no standalone file to read from, only bytes already extracted
from the PDF. `page.images` re-encodes embedded images as JPEG
internally (visible in `image_file.name` ending in `.jpg`), so the MIME
type passed to `Part.from_bytes` needs to say `image/jpeg`, not
`image/png`, matching what's actually in the bytes.

## Running it

```bash
uv run python lessons/multimodal_rag/02_intermediate/17_extracting_images_from_a_pdf/lesson.py
```

## Expected output

```
circuit-board-notebook.pdf, page 1: 1 embedded image found

Caption:
<a detailed description mentioning "2 Hz" and the 555 timer>
```

## Checkpoint

- `pypdf`'s `page.images` extracts a PDF page's embedded images as raw
  bytes plus a filename hinting at the encoding (usually JPEG), no new
  top-level dependency needed for this project, `pypdf` is already
  present transitively.
- Once bytes are extracted, everything downstream (captioning,
  embedding, retrieval, generation) is identical to a standalone image
  file; a PDF is just one more place bytes can come from.
- `DOCUMENT_FIGURES` (Lesson 10)'s hand-maintained figure-order mapping
  is exactly what a real PDF-based pipeline replaces: figure order
  falls naturally out of the order images appear on each page, instead
  of being written down by hand.

If anything here still feels unclear, ask before moving to Lesson 18.
