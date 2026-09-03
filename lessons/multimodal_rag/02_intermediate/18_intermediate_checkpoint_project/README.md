# Lesson 18: Intermediate Checkpoint - Notes-and-Diagrams Search Assistant

## What this is

No new concepts in this lesson. This is a checkpoint: a small, real
script built entirely out of ideas from Lessons 10 through 17, combined
into one thing. If you can read `lesson.py` and understand why every
piece is there, you've mastered the Intermediate tier. If any piece
feels unfamiliar, that's a sign to revisit the lesson it came from
before continuing to Advanced.

## What it does

Builds the complete mixed store: five notes, four standalone image
figures (with `parent_document`/`figure_number` metadata, Lesson 10),
and one image extracted from `circuit-board-notebook.pdf` (Lesson 17),
ten records in total, all carrying explicit `modality` metadata (Lesson
11). Answers three questions using balanced retrieval (Lesson 13) and a
modality-aware citation prompt (Lesson 14).

## Where each piece came from

```python
def extract_images_from_pdf(pdf_path: Path) -> list[bytes]:
    ...
```
Lesson 17, unchanged: pull the one embedded image out of
`circuit-board-notebook.pdf`, captioned the same way any other image
is.

```python
{"text": caption, "embedding": vector, "source": ..., "modality": "image",
 "image_path": ..., "parent_document": ..., "figure_number": ...}
```
Lessons 10-11's record shape: modality metadata plus the document/figure
this image belongs to, whether the image came from a standalone `.png`
or from inside a PDF page.

```python
def retrieve_balanced(query, store, k_text, k_image):
    ...
```
Lesson 13, unchanged: rank each modality separately, guarantee a mix.

```python
def generate_answer(query, retrieved):
    ...
```
Lesson 14, unchanged: build `contents` with modality-labeled sources,
require citations naming both file and modality.

## Running it

```bash
uv run python lessons/multimodal_rag/02_intermediate/18_intermediate_checkpoint_project/lesson.py
```

You should see: a bike question answered from text, a torque-spec
question answered by looking at an image directly, and a 555-timer
frequency question answered from the image embedded inside the PDF
fixture, each cited with both its file and its modality.

## Try this yourself

Without looking anything up:

- Add a new figure to `DOCUMENT_FIGURES` for a note that currently has
  none (`terrarium.md`, say), pointing at any existing image file as a
  stand-in. Does a question about that note now correctly retrieve and
  cite the "wrong" image, showing the metadata is doing exactly what
  you told it to, nothing more?
- Change `k_image` to `0` in `retrieve_balanced` for the PDF question.
  Confirm the answer degrades to an honest "I don't know" instead of a
  hallucinated frequency, then set it back.
- Ask a question with no correct answer anywhere in the fixtures (like
  `naive_rag`'s "capital of France" test). Confirm the modality-aware
  prompt still refuses to guess.

If you can make these changes confidently, you're ready for the
Advanced tier, starting at Lesson 19.
