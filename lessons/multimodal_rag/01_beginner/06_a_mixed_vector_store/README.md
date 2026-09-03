# Lesson 6: A Mixed Vector Store

## Where we left off

Lessons 4-5 turned one image into an embedded caption. This lesson
builds the whole store: every text note in `fixtures/notes/` embedded
the way `naive_rag` always has, plus every image in `fixtures/images/`
captioned (Lesson 4) and embedded (Lesson 5), all combined into **one**
Python list. Nothing downstream (Lesson 7's retrieval especially) will
be able to tell, just from looking at the list, which records started
as text and which started as an image, and that's the intended result:
a single ranked search over everything.

## The code, piece by piece

```python
def build_text_records() -> list[dict]:
    paths = sorted(NOTES_DIR.glob("*.md"))
    texts = [path.read_text() for path in paths]
    vectors = embed_texts(texts)
    return [
        {"text": text, "embedding": vector, "source": path.name, "image_path": None}
        for path, text, vector in zip(paths, texts, vectors)
    ]
```

`naive_rag`'s exact record shape (`text`, `embedding`, `source`), plus
one new field, `image_path`, set to `None` here because a text record
has no image behind it. That field exists for one reason: Lesson 8
needs to know, once a record is retrieved, whether there's an original
image worth re-attaching to the generation call, or whether the
record's `text` (a real document chunk) is already the whole answer.

```python
def build_image_records() -> list[dict]:
    paths = sorted(IMAGES_DIR.glob("*.png"))
    captions = [caption_image(path) for path in paths]
    vectors = embed_texts(captions)
    return [
        {"text": caption, "embedding": vector, "source": path.name, "image_path": path}
        for path, caption, vector in zip(paths, captions, vectors)
    ]
```

The mirror image of the function above: `text` holds the *caption*, not
raw document text, but the field is still called `text`, on purpose,
because from Lesson 7's retrieval code onward, nothing needs to
distinguish "text chunk" from "caption text", they're both just text to
rank by similarity. `image_path` is set here, pointing back to the
original file.

```python
store = build_text_records() + build_image_records()
```

One list, plain Python list concatenation. This is the entire "mixed"
part of "mixed vector store": no new data structure, no tagging step
required to make retrieval work across both, just two lists of records
built by different functions, sharing one shape.

## Running it

```bash
uv run python lessons/multimodal_rag/01_beginner/06_a_mixed_vector_store/lesson.py
```

## Expected output

```
Text records: 5 (bike-repair.md, circuit-board.md, home-observatory.md, sourdough-starter.md, terrarium.md)
Image records: 4 (derailleur-hanger-diagram.png, observatory-finder-scope.png, observatory-mount-wiring.png, starter-jar-markings.png)
Mixed store: 9 records total
```

## Checkpoint

- A mixed vector store is not a new kind of data structure, it's the
  same list-of-records shape `naive_rag` used, with image captions
  added as records alongside text chunks.
- `image_path` is the one new field, `None` for a text record, a real
  path for an image record, carried along so a later stage (Lesson 8)
  can re-attach the original image, not needed by retrieval itself.
- Captioning every image happens once, up front, at store-build time,
  the same "build once, query many times" shape `naive_rag` Lesson 5
  established for embedding.

If anything here still feels unclear, ask before moving to Lesson 7.
