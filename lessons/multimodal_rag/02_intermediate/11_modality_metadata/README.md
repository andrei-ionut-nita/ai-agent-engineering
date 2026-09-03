# Lesson 11: Modality Metadata

## Where we left off

Since Lesson 6, code has checked `record["image_path"] is not None` to
tell a caption record from a text record. That works, but it's an
implicit convention, "not `None`" standing in for a real category. This
lesson makes it explicit: every record gets a `"modality"` field, either
`"text"` or `"image"`, plus a `source` field that's always the file the
record actually came from. This is `naive_rag` Lesson 12's move
(tagging every chunk with its source file) applied to the one new
dimension this course adds: not just *which file*, but *which kind of
file*.

## Why this needs its own field, not just inference

`image_path is not None` works today because there are exactly two
kinds of record. The moment a third modality shows up (audio
transcripts, say, in some future course), or the moment some other code
path needs to filter "give me only images" without also caring about
paths, an implicit check scattered across every function becomes a
liability: it's has to be reimplemented, correctly, everywhere it's
needed. An explicit `"modality"` field is a single source of truth,
`record["modality"] == "image"` reads the same everywhere, and Lesson 21
depends on exactly this field existing when it becomes a real chromadb
`where` filter.

## The code, piece by piece

```python
text_records = [
    {
        "text": text,
        "embedding": vector,
        "source": path.name,
        "modality": "text",
        "image_path": None,
    }
    for path, text, vector in zip(paths, texts, vectors)
]
```

One added key, `"modality": "text"`, a constant for every record built
this way. `image_path` stays for now (Lesson 8 still needs it to
re-attach a real file), `modality` doesn't replace it, it names what
`image_path is not None` was already implying.

```python
image_records = [
    {..., "modality": "image", "image_path": path, "figure_number": n}
    for ...
]
```

Same idea for image records, `"modality": "image"` alongside Lesson
10's `parent_document`/`figure_number` fields. From here on, every
record in this course carries `modality` explicitly.

## Running it

```bash
uv run python lessons/multimodal_rag/02_intermediate/11_modality_metadata/lesson.py
```

## Expected output

```
Mixed store: 9 records
  text : 5 records (bike-repair.md, circuit-board.md, home-observatory.md, sourdough-starter.md, terrarium.md)
  image: 4 records (derailleur-hanger-diagram.png, observatory-finder-scope.png, observatory-mount-wiring.png, starter-jar-markings.png)
```

## Checkpoint

- **`modality`**: an explicit `"text"` or `"image"` field on every
  record, replacing the implicit `image_path is not None` convention
  used since Lesson 6.
- Naming something explicitly, instead of relying on a related field's
  presence to imply it, is worth the extra line the moment more than
  one piece of code needs to check it, or a third category might show
  up later.
- This field is what Lesson 21's chromadb `where={"modality": "image"}`
  filter and Lesson 13's k-balancing both key off directly.

If anything here still feels unclear, ask before moving to Lesson 12.
