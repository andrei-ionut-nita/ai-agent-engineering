# Course index

A linear, one-concept-per-lesson path through **docling**, the IBM /
LF AI open-source document-conversion library. Docling turns PDF,
DOCX, PPTX, HTML, and images into structured Markdown or JSON, with a
real layout model underneath: it detects headings, reading order,
tables, and pictures instead of just extracting a stream of text. Do
these in order, top to bottom, each lesson folder has a `README.md`
(read first) and a `lesson.py` (run second). Don't move to the next
lesson until the current one's checkpoint questions feel solid.

## Where this fits next to markitdown and liteparse

If you've done the [markitdown](../markitdown/) or [liteparse](../liteparse/)
courses, docling will feel like a third answer to the same question,
"turn this document into something an LLM can read". markitdown
optimizes for breadth and simplicity: many formats, one `.convert()`
call, minimal setup. liteparse optimizes for PDF fidelity: layout,
forms, OCR, all fast. docling sits at the deep end of that same axis
and adds a real trained layout model, TableFormer table structure
recognition, and a chunker built specifically for RAG pipelines, at
the cost of heavier dependencies and slower conversions. Lesson 17
compares all three directly, once you've used each one enough to have
an informed opinion. Nothing here requires the other two courses as a
hard prerequisite, but the comparison lesson reads better if you've
done at least the beginner tier of one of them.

Docling also composes well with [llamaindex](../llamaindex/) and
LangChain, since its whole job ends at producing structured text or
JSON chunks, exactly the input those libraries expect. Lesson 16 makes
that connection explicit.

## Setup

No API key or network account is required for the core conversion
pipeline, docling's layout, table, and OCR models run locally (the
first run of any lesson downloads a few hundred megabytes of model
weights the first time each model is used, then reuses the local
cache). Lesson 16 makes real Gemini API calls and needs a
`GOOGLE_API_KEY` in a `.env` file at the project root, the same key
used throughout this repo (get a free one at
[aistudio.google.com/apikey](https://aistudio.google.com/apikey)).

From the project root:

```bash
uv run python lessons/docling/<tier>/<NN>_<name>/lesson.py
```

The first lesson you run will take noticeably longer than the rest,
that's the one-time model download, not a hang.

## Beginner: your first conversions, and what `DoclingDocument` actually holds

| # | Lesson | Concept |
|---|--------|---------|
| 01 | [what_is_docling](01_beginner/01_what_is_docling/) | What docling is, and how it differs from markitdown/liteparse |
| 02 | [first_convert_call](01_beginner/02_first_convert_call/) | `DocumentConverter().convert()`, `export_to_markdown()` |
| 03 | [the_docling_document](01_beginner/03_the_docling_document/) | `DoclingDocument`: texts, tables, pictures, groups |
| 04 | [converting_docx_and_pptx](01_beginner/04_converting_docx_and_pptx/) | One converter, many `InputFormat`s |
| 05 | [reading_structure](01_beginner/05_reading_structure/) | Headings, sections, and `export_to_text()` |
| 06 | [beginner_checkpoint_project](01_beginner/06_beginner_checkpoint_project/) | **Checkpoint:** convert a folder of mixed documents |

## Intermediate: pipeline options, tables, OCR, and chunking for RAG

| # | Lesson | Concept |
|---|--------|---------|
| 07 | [pdf_pipeline_options](02_intermediate/07_pdf_pipeline_options/) | `PdfPipelineOptions`, `format_options`, `PdfFormatOption` |
| 08 | [table_structure_with_tableformer](02_intermediate/08_table_structure_with_tableformer/) | `TableFormerMode.FAST` vs `ACCURATE`, `export_to_dataframe()` |
| 09 | [ocr_for_scanned_pdfs](02_intermediate/09_ocr_for_scanned_pdfs/) | `do_ocr`, `EasyOcrOptions`, image-only PDFs |
| 10 | [images_and_picture_extraction](02_intermediate/10_images_and_picture_extraction/) | `generate_picture_images`, saving extracted figures |
| 11 | [chunking_with_hybridchunker](02_intermediate/11_chunking_with_hybridchunker/) | `HybridChunker`, tokenizer-aware chunk boundaries |
| 12 | [exporting_to_json](02_intermediate/12_exporting_to_json/) | `export_to_dict()`, round-tripping a `DoclingDocument` |
| 13 | [intermediate_checkpoint_project](02_intermediate/13_intermediate_checkpoint_project/) | **Checkpoint:** table + OCR + chunked JSON pipeline |

## Advanced: enrichment, performance, and closing the loop with LlamaIndex

| # | Lesson | Concept |
|---|--------|---------|
| 14 | [formula_and_code_enrichment](03_advanced/14_formula_and_code_enrichment/) | `do_formula_enrichment`, `do_code_enrichment` |
| 15 | [batch_conversion_and_performance](03_advanced/15_batch_conversion_and_performance/) | `convert_all()`, reusing one `DocumentConverter` |
| 16 | [feeding_docling_into_llamaindex](03_advanced/16_feeding_docling_into_llamaindex/) | `HybridChunker` output into a LlamaIndex `VectorStoreIndex` |
| 17 | [comparing_docling_markitdown_liteparse](03_advanced/17_comparing_docling_markitdown_liteparse/) | Fidelity vs. speed vs. simplicity, tested, not just claimed |
| 18 | [advanced_capstone_project](03_advanced/18_advanced_capstone_project/) | **Capstone:** a folder-to-queryable-chunks RAG ingestion pipeline |
