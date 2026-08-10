# Course index

A linear, one-concept-per-lesson path through **LiteParse**, a local,
open-source, Rust-backed PDF parser. Do these in order, top to bottom,
each lesson folder has a `README.md` (read first) and a `lesson.py`
(run second). Don't move to the next lesson until the current one's
checkpoint questions feel solid.

LiteParse solves the same problem hosted document-parsing APIs solve,
turning a PDF into clean, structured text, but as a Python import
instead of a network call. Contrast it with **LlamaParse**, LlamaIndex's
own hosted cloud parsing service: same category of problem, opposite
architecture. LiteParse's actual parsing work runs in a compiled Rust
extension module inside the package itself, so there's no API key, no
per-page bill, and no document ever leaves your machine.

This repo also has a [markitdown](../markitdown/) course. MarkItDown
covers far more file formats (Word, Excel, HTML, images, and more) but
goes shallower on PDF-specific layout. LiteParse is PDF-only, but with
real depth: per-page layout, form fields, annotations, structure trees,
and OCR fallback. The full head-to-head comparison lives in MarkItDown's
own course, not here.

No hard prerequisite course is required. Lessons 13 and 14 do assume
basic familiarity with the [llamaindex](../llamaindex/) course, Lessons
1-4 (`Document`, `VectorStoreIndex`), the same way the
[ollama](../ollama/) course notes its own soft prerequisite on
[langchain](../langchain/).

Setup: no new API key or service is required for this course. LiteParse
is already listed in this project's root `pyproject.toml` and installed
into `.venv` via `uv sync`, and every sample PDF this course uses
already ships pre-built in `sample_data/`. (Those fixtures were
originally built with LibreOffice, only needed once, to generate the
PDFs from plain-text sources in `sample_data/_src/`, not something you
need to repeat.) Lessons 13 and 14 do call Gemini, through this
project's existing `GOOGLE_API_KEY` in `.env`, the same key every other
Gemini-backed course in this repo uses. From the project root:

```bash
uv run python lessons/liteparse/<tier>/<NN>_<name>/lesson.py
```

## Beginner: your first parses

| # | Lesson | Concept |
|---|--------|---------|
| 01 | [what_is_liteparse](01_beginner/01_what_is_liteparse/) | Local, Rust-backed parsing vs hosted parsing APIs like LlamaParse |
| 02 | [first_parse_call](01_beginner/02_first_parse_call/) | `LiteParse()`, `.parse(path)`, `.text` |
| 03 | [parse_config_options](01_beginner/03_parse_config_options/) | `ocr_enabled`, `max_pages`, `target_pages`, `output_format`, `password` |
| 04 | [pages_and_layout](01_beginner/04_pages_and_layout/) | `result.pages`, per-page `ParsedPage`, `text_items` |
| 05 | [beginner_checkpoint_project](01_beginner/05_beginner_checkpoint_project/) | **Checkpoint:** batch-parse `sample_data/` to `.txt` files with a per-file summary |

## Intermediate: structured extraction and OCR

| # | Lesson | Concept |
|---|--------|---------|
| 06 | [tables_and_form_fields](02_intermediate/06_tables_and_form_fields/) | `extract_form_fields=True`, `FormField`, real AcroForm widgets |
| 07 | [images_and_screenshots](02_intermediate/07_images_and_screenshots/) | `extract_images`, `screenshot()`, `detect_screenshot_rects` |
| 08 | [ocr_for_scanned_documents](02_intermediate/08_ocr_for_scanned_documents/) | The `ocr_enabled` contrast on a genuinely scanned PDF, `is_complex()` |
| 09 | [document_metadata_and_annotations](02_intermediate/09_document_metadata_and_annotations/) | `extract_document_metadata`, `DocumentMetadata`, `extract_annotations`, `extract_links` |
| 10 | [structure_tree_and_accessibility](02_intermediate/10_structure_tree_and_accessibility/) | `extract_structure_tree`, tagged PDF, why screen readers need it |
| 11 | [intermediate_checkpoint_project](02_intermediate/11_intermediate_checkpoint_project/) | **Checkpoint:** auto-detect which PDFs need OCR, unify a mixed batch |

## Advanced: concurrency and a real LlamaIndex pipeline

| # | Lesson | Concept |
|---|--------|---------|
| 12 | [batch_and_concurrency](03_advanced/12_batch_and_concurrency/) | `num_workers`, timing a threaded batch parse |
| 13 | [feeding_liteparse_into_llamaindex](03_advanced/13_feeding_liteparse_into_llamaindex/) | LiteParse text into `llama_index.core.Document`, `VectorStoreIndex`, querying with Gemini |
| 14 | [advanced_capstone_project](03_advanced/14_advanced_capstone_project/) | **Capstone:** mixed native+scanned folder, OCR fallback, LlamaIndex index, Gemini-answered queries, no cloud parsing API anywhere |
