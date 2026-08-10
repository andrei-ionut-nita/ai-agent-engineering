# Lesson 8: `StreamInfo` and format hints

## Why this matters more than "auto-detection usually works"

Lesson 4 used `file_extension=".docx"` without explaining much. The
interesting part isn't that hints exist, MarkItDown's auto-detection,
via a small ML content classifier called `magika`, is genuinely good.
The interesting part is what happens when a hint is *wrong*: it
doesn't raise an error. MarkItDown trusts an explicit hint over its
own content-based guess, so a wrong hint routes the file to the wrong
converter, and the conversion still "succeeds", just with worse
output, silently.

## `file_extension` is shorthand for a `StreamInfo`

```python
from markitdown._stream_info import StreamInfo

stream_info = StreamInfo(
    mimetype="text/csv",
    extension=".csv",
    filename="expenses.csv",
)
md.convert_stream(file_obj, stream_info=stream_info)
```

`StreamInfo` is a small frozen dataclass carrying whatever metadata
you have about a stream: `mimetype`, `extension`, `charset`,
`filename`, `local_path`, `url`. `file_extension="..."` in
`convert_stream()` is a convenience that builds one of these under the
hood with just the extension set. Reach for the fuller `StreamInfo`
when you have more than one piece of metadata available at once, for
example both a `Content-Type` header and a filename from an HTTP
upload's `Content-Disposition` header.

## Four scenarios, one input

This lesson converts the exact same CSV bytes four ways to make the
contrast concrete:

| Scenario | What MarkItDown does | Result |
|---|---|---|
| No hint | `magika` classifies the raw bytes as CSV | Correct: Markdown table |
| `file_extension=".csv"` | Explicit, matches magika's own guess | Correct: Markdown table |
| `file_extension=".txt"` (wrong) | Trusts the hint, routes to `PlainTextConverter` | Silently wrong: raw comma-separated text, structure lost |
| Full `StreamInfo(mimetype=, extension=, filename=)` | Same as the correct hint, more metadata attached | Correct: Markdown table |

The `.txt` row is the one to actually notice: nothing raised, nothing
warned, the output just quietly lost its table structure. If a
pipeline hardcodes a format hint based on something unreliable (a
user-supplied filename, say), this is the class of bug it can produce.

## The code, piece by piece

```python
result_no_hint = md.convert_stream(io.BytesIO(CSV_BYTES))
```

No `file_extension`, no `stream_info`, MarkItDown falls back entirely
to `magika`'s content classification.

```python
result_wrong_hint = md.convert_stream(io.BytesIO(CSV_BYTES), file_extension=".txt")
```

The wrong hint. Confirms, on real output, that MarkItDown does not
attempt to reconcile a stated extension against the content it's
actually looking at.

## Running it

```bash
uv run python lessons/markitdown/02_intermediate/08_stream_info_and_format_hints/lesson.py
```

## Expected output

```
=== No hint: magika content-detection alone ===

| Date | Category | Amount |
| --- | --- | --- |
| 2026-06-02 | Travel | 412.50 |
| 2026-06-03 | Meals | 96.20 |

=== Correct hint: file_extension='.csv' ===

| Date | Category | Amount |
| --- | --- | --- |
| 2026-06-02 | Travel | 412.50 |
| 2026-06-03 | Meals | 96.20 |

=== WRONG hint: file_extension='.txt' (silently loses structure) ===

Date,Category,Amount
2026-06-02,Travel,412.50
2026-06-03,Meals,96.20


=== Explicit StreamInfo: mimetype + extension + filename ===

| Date | Category | Amount |
| --- | --- | --- |
| 2026-06-02 | Travel | 412.50 |
| 2026-06-03 | Meals | 96.20 |
```

## Checkpoint

- **`StreamInfo`**: a dataclass carrying `mimetype`, `extension`,
  `charset`, `filename`, and more, `file_extension="..."` in
  `convert_stream()` is shorthand for a `StreamInfo` with just the
  extension set.
- **Auto-detection (`magika`)**: usually gets it right from content
  alone, no hint needed for well-formed files.
- **A wrong hint doesn't error, it silently degrades**: MarkItDown
  trusts an explicit hint over its own content guess, so bad metadata
  produces bad, unannounced output, not an exception you'd catch.
- **When to hint explicitly**: whenever you have reliable metadata
  (a real `Content-Type` header, a trusted filename) and want to skip
  content-sniffing, or when a stream's content alone is genuinely
  ambiguous.

If anything here still feels unclear, ask before moving to Lesson 9.
