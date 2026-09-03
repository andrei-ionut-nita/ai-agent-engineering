# Lesson 10: Captioning Multiple Images per Document

## Where we left off

Every image so far has stood alone. `home-observatory.md` breaks that
assumption on purpose: it has *two* figures,
`observatory-finder-scope.png` (fig. 1) and `observatory-mount-wiring.png`
(fig. 2), both belonging to the same source document. This lesson
handles that: captioning and retrieval both already work per-image
(Lessons 4 and 7), the only new idea is bookkeeping, keeping each
image's figure number and parent document attached to its record, so
two images from the same document don't get confused with each other or
with a third document's own images.

## The code, piece by piece

```python
DOCUMENT_FIGURES = {
    "home-observatory.md": ["observatory-finder-scope.png", "observatory-mount-wiring.png"],
    "sourdough-starter.md": ["starter-jar-markings.png"],
    "bike-repair.md": ["derailleur-hanger-diagram.png"],
}
```

An explicit map from a note's filename to the ordered list of images
that belong to it. This is hand-maintained here, on purpose, standing
in for what a real ingestion pipeline usually gets from a document's
own structure (a PDF's embedded figures, in order, which Lesson 17
handles directly). Order in the list is the figure number, `fig. 1`,
`fig. 2`, and so on, matching how the fixture notes themselves refer to
"fig. 1" and "fig. 2" in `fixtures/README.md`.

```python
for figure_number, image_path in enumerate(image_paths, start=1):
    caption = caption_image(image_path)
    records.append({
        "text": caption,
        "embedding": ...,
        "source": image_path.name,
        "image_path": image_path,
        "parent_document": document_name,
        "figure_number": figure_number,
    })
```

Two new fields per image record: `parent_document` (which note this
figure belongs to) and `figure_number` (its position within that
document). Neither changes how retrieval or generation work, both
already only look at `text`, `embedding`, and `image_path`; these two
fields exist purely so an answer can eventually say "fig. 2 of
home-observatory.md" instead of just the image's raw filename, useful
once a document has more than one figure and a citation needs to be
specific about which one.

## Running it

```bash
uv run python lessons/multimodal_rag/02_intermediate/10_captioning_multiple_images_per_document/lesson.py
```

## Expected output

```
home-observatory.md has 2 figures:
  fig. 1: observatory-finder-scope.png
  fig. 2: observatory-mount-wiring.png

Query: "What color are the motor cables on the mount?"
Top match: observatory-mount-wiring.png (home-observatory.md, fig. 2)
```

## Checkpoint

- A document can have more than one image; each one is still captioned
  and embedded independently (Lessons 4-5 unchanged), the new part is
  tracking which document and which position each one came from.
- `parent_document` and `figure_number` are citation metadata, they
  don't affect retrieval ranking at all, only what a final answer can
  say about where a fact came from.
- `DOCUMENT_FIGURES` here is hand-built; Lesson 17 shows a case (images
  embedded in a PDF) where this mapping falls out of the document's own
  structure instead of being written by hand.

If anything here still feels unclear, ask before moving to Lesson 11.
