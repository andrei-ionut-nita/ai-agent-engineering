# Lesson 10: extracting pictures as real image files

## What the `<!-- image -->` placeholder was hiding

Lesson 3 showed `doc.pictures` has one entry for `quarterly_report.pdf`'s
chart, and `export_to_markdown()` renders it as a bare
`<!-- image -->` comment. docling detected exactly where that picture
is on the page, it just doesn't render pixels for it unless asked to,
rendering costs memory and time you might not want to pay if all you
need is the Markdown text. This lesson asks for the pixels.

## `generate_picture_images` and `images_scale`

```python
options = PdfPipelineOptions()
options.generate_picture_images = True
options.images_scale = 2.0
```

`generate_picture_images=True` tells the pipeline to render each
detected picture region as an actual raster image, not just record its
bounding box. `images_scale` controls the resolution relative to the
PDF page's own coordinate space, `2.0` roughly doubles the pixel
dimensions you'd get from the page's native size, useful when a
downstream step (a caption model, a human reviewer) needs more detail
than the PDF's default rendering resolution provides.

## `picture.get_image(doc)`

```python
image = picture.get_image(doc)
image.save(output_path)
```

`get_image()` needs the owning `DoclingDocument` passed in, the same
pattern as `export_to_dataframe()` in Lesson 8, a picture item's
rendered content is resolved relative to the document it belongs to.
It returns a plain PIL `Image`, whatever you'd normally do with a PIL
image (`.save()`, `.resize()`, feed it to a vision model) works here
unchanged.

## Running it

```bash
uv run python lessons/docling/02_intermediate/10_images_and_picture_extraction/lesson.py
```

## Expected output

```
Pictures detected: 1
  picture 0: 505x297 px -> picture_0.png
```

An `extracted_images/` subfolder now exists alongside this README with
`picture_0.png` in it, the actual chart from `quarterly_report.pdf`,
extracted as a standalone file.

## Checkpoint

- **Picture detection and picture rendering are separate steps**:
  `doc.pictures` always lists detected picture regions, rendering
  their pixels is opt-in via `generate_picture_images`.
- **`images_scale`**: controls output resolution relative to the PDF's
  native page size.
- **`picture.get_image(doc)`**: returns a plain PIL `Image`, rendered
  from exactly that picture's bounding box, not the whole page.

If anything here still feels unclear, ask before moving to Lesson 11.
