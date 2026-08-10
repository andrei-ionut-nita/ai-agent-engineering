# Lesson 1: What is LiteParse?

## Hosted parsing APIs vs a local, Rust-backed library

PDFs are one of the messiest formats an AI pipeline has to deal with:
text isn't stored in reading order, tables aren't really tables, scanned
pages have no text layer at all. A whole category of products exists
just to turn a PDF into clean text or Markdown for you, LlamaIndex's own
hosted **LlamaParse** service being a well-known example. You upload a
file, their servers (often running a mix of layout models and OCR) parse
it, and you get structured text back over the network.

LiteParse solves the same problem differently: it's a normal Python
package (`pip install liteparse` / already in this project's
`pyproject.toml`) with a compiled Rust extension module inside it. When
you call `.parse()`, the PDF-parsing logic, and optionally OCR, runs
**in this process**, using your own CPU. There is no upload, no API key,
no per-page bill, and no dependency on a remote service staying up.

| | Hosted parsing API (e.g. LlamaParse) | LiteParse (this course) |
|---|---|---|
| Where it runs | A cloud service | This process, on your machine |
| Needs network | Every single call, plus the file upload | Never |
| API key | Yes | No |
| Cost | Per-page or per-document pricing | Free, open source |
| Privacy | Your document leaves your machine | It never does |
| Speed ceiling | Bounded by upload size and provider queue | Bounded by your CPU |
| Layout/table intelligence | Often stronger (large models behind the API) | Solid for text, tables, forms; no LLM reasoning built in |

Neither is strictly better. A hosted API can throw a large vision-language
model at a genuinely gnarly scanned contract; LiteParse gives you fast,
free, offline extraction for the very common case of "I have a folder of
PDFs and I need their text," which is most of what a RAG pipeline or
document-processing agent actually needs.

This repo also has a [markitdown](../../../markitdown/) course. MarkItDown
covers more file formats (Word, Excel, PowerPoint, HTML, images, audio
transcripts, and more) but is shallower on PDF-specific layout details.
LiteParse is the opposite trade: PDF-only, but with real depth, per-page
layout, form fields, annotations, structure trees, and OCR fallback, all
covered in this course. If you want the full side-by-side comparison,
that lives in MarkItDown's own course, not here.

## The code, piece by piece

```python
import liteparse
```

That's the entire setup. No client object to authenticate, no service to
start in the background the way the [ollama](../../../ollama/) course
needed a separate application running. `liteparse` is installed like any
other Python dependency and works the moment it's imported.

```python
print(f"liteparse version: {liteparse.__version__}")
```

Confirms the package is actually importable and reports its version, a
quick sanity check before the rest of the course builds on it.

```python
parser = liteparse.LiteParse(ocr_enabled=False, quiet=True)
result = parser.parse("lessons/liteparse/sample_data/employee_handbook.pdf")
```

A first, minimal parse. `ocr_enabled=False` is set here on purpose, since
this document has a real text layer and doesn't need OCR at all (Lesson
8 covers exactly when OCR does and doesn't kick in); `quiet=True`
suppresses LiteParse's per-stage timing logs so this lesson's own timing
print is the only thing on screen. Lesson 2 covers `.parse()` and
`.text` properly.

The timing wrapper around the call is the point of this lesson: parsing
a page takes single-digit milliseconds, entirely on-CPU, because the
actual work happens in the compiled Rust extension module bundled inside
the `liteparse` package, not in interpreted Python and not over a
network socket.

## Running it

```bash
uv run python lessons/liteparse/01_beginner/01_what_is_liteparse/lesson.py
```

## Expected output

```
Cloud document-parsing APIs vs LiteParse (this course):
  Where it runs: A hosted parsing service (cloud) vs this process, in-memory (local)
  Network required: Yes, every call, plus a file upload vs no, never
  API key required: Yes vs no, it's just a Python import
  Cost: Per-page or per-document pricing vs free, open source
  Privacy: Your PDF leaves your machine vs it never does
  Speed: Bounded by upload size and provider queue vs bounded by your CPU

liteparse version: 2.11.1

Parsed employee_handbook.pdf in 5.5ms, no network call made:
  1 page(s), 1070 characters extracted
```

The exact millisecond count depends on your machine and will vary
between runs; it will consistently be small (single-to-low-double-digit
milliseconds) since no network is involved.

## Checkpoint

- **LiteParse**: a local, Rust-backed, open-source Python library for
  parsing PDFs, no API key, no network call, no cloud service.
- **"Rust-backed"**: the actual parsing work runs in a compiled native
  extension module, which is why it's fast even on a laptop CPU.
- **Hosted parsing APIs** (like LlamaParse): a different trade, network
  round-trip and a bill per document, in exchange for potentially
  stronger layout/vision-model intelligence on hard documents.
- **vs MarkItDown**: broader format coverage there, deeper PDF-specific
  layout/forms/OCR handling here, not a strict superset either way.

If anything here still feels unclear, ask before moving to Lesson 2.
