# Lesson 2: the first `.convert()` call

## The whole library, in two lines

```python
md = MarkItDown()
result = md.convert("path/to/file")
```

That's it, that's the core interface. Everything else in this course,
office documents, streams, URLs, images with LLM captioning, custom
converters, is a variation on those two lines. Get comfortable with
this shape first.

## What `.convert()` returns

`.convert()` doesn't return a string, it returns a
`DocumentConverterResult` object with a few attributes:

| Attribute | What it is |
|---|---|
| `.markdown` | The converted Markdown text. The main thing you want. |
| `.text_content` | A soft-deprecated alias for `.markdown`, same string, kept for readability and older code. |
| `.title` | Optional title metadata, populated when the source format has an obvious one (docx/pptx document properties), `None` otherwise. |

## Format auto-detection

Notice the call was just `md.convert(path)`, no `format="txt"`
argument anywhere. MarkItDown inspects the file's extension and
content to figure out which of its registered converters should
handle it. This "just works" behavior is convenient, but it isn't
magic, Lesson 8 covers what happens when auto-detection needs help
(a stream with no filename, an ambiguous extension) and how to hint it
with `StreamInfo`.

## The code, piece by piece

```python
md = MarkItDown()
result = md.convert(FIXTURES_DIR / "release_notes.txt")
```

`.convert()` accepts a `Path` object directly, no need to call `str()`
on it first.

```python
result.text_content == result.markdown
```

Confirms these are literally the same string, not two independently
computed values. Either name is fine to use; this course generally
prefers `.markdown` since it's the current, non-deprecated name, but
you'll see `.text_content` in MarkItDown's own examples and in some
existing lesson-plan notes.

## Running it

```bash
uv run python lessons/markitdown/01_beginner/02_first_convert_call/lesson.py
```

## Expected output

```
Converted: release_notes.txt
Result type: DocumentConverterResult

.text_content == .markdown: True

Full converted Markdown:
----------------------------------------
Release Notes: TrailLight App v1.3

- Added offline mode so brightness settings sync once reconnected
- Fixed a bug where battery percentage rounded incorrectly on Android
- Improved pairing time with the lantern's Bluetooth module
- Minor translation fixes for the Spanish and French locales

----------------------------------------

Title: None
```

`release_notes.txt` is a plain text file, so `.title` is `None`,
there's no metadata field for a title in a `.txt` file. Lesson 3
converts formats that sometimes do populate it.

## Checkpoint

- **The core call**: `MarkItDown().convert(path)` returns a
  `DocumentConverterResult`.
- **`.markdown` / `.text_content`**: same string, two names, prefer
  `.markdown` in new code.
- **`.title`**: optional, populated only when the source format has
  obvious title metadata.
- **No format argument needed**: MarkItDown auto-detects from
  extension and content; Lesson 8 covers when that needs a hint.

If anything here still feels unclear, ask before moving to Lesson 3.
