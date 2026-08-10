# Course index

A linear, one-concept-per-lesson path through **MarkItDown**,
Microsoft's open-source library for converting a wide range of file
formats, Word, PowerPoint, Excel, PDF, images, plain text, HTML, and
more, into Markdown so an LLM can actually read them. Do these in
order, top to bottom, each lesson folder has a `README.md` (read
first) and a `lesson.py` (run second). Don't move to the next lesson
until the current one's checkpoint questions feel solid.

This course has no hard prerequisite and can be started cold. Lessons
10 and 11 assume basic familiarity with
[`lessons/llamaindex/`](../llamaindex/) (Lessons 1-4: `Settings`,
`Document`, `VectorStoreIndex`, query engines) and the existence of
[`lessons/liteparse/`](../liteparse/), the same way
[`lessons/ollama/README.md`](../ollama/README.md) notes its
`lessons/langchain/` prerequisite, but neither is required to start
Lesson 1.

Setup: no new API key or service needed. `markitdown[all]` is already
listed in this project's `pyproject.toml` and installed via `uv sync`.
Lessons 6, 10, and 12 use this project's existing `GOOGLE_API_KEY`
(already in `.env`) for LLM image captioning and LlamaIndex embeddings
and generation, the same key every other course in this repo uses,
nothing new to configure. This course's fixture files under
`fixtures/` (a `.docx`, `.pptx`, `.xlsx`, `.pdf`, `.txt`, and `.png`)
were built ahead of time as this course's sample data, the tools used
to build them were dev-time only and aren't part of any lesson. From
the project root:

```bash
uv run python lessons/markitdown/<tier>/<NN>_<name>/lesson.py
```

## Beginner: the core conversion call

| # | Lesson | Concept |
|---|--------|---------|
| 01 | [what_is_markitdown](01_beginner/01_what_is_markitdown/) | Broad-format-conversion positioning, `markitdown[all]` vs base install, MarkItDown vs LiteParse |
| 02 | [first_convert_call](01_beginner/02_first_convert_call/) | `MarkItDown()`, `.convert(path)`, `.text_content` / `.markdown` |
| 03 | [converting_office_documents](01_beginner/03_converting_office_documents/) | docx/pptx/xlsx fixtures, how source structure maps to Markdown |
| 04 | [converting_from_streams_and_urls](01_beginner/04_converting_from_streams_and_urls/) | `convert_stream()` on an open file handle, `convert_url()` against a live page |
| 05 | [beginner_checkpoint_project](01_beginner/05_beginner_checkpoint_project/) | **Checkpoint:** convert a whole folder to `.md` files, source-format-to-length summary |

## Intermediate: images, extensibility, and format hints

| # | Lesson | Concept |
|---|--------|---------|
| 06 | [images_and_llm_captioning](02_intermediate/06_images_and_llm_captioning/) | `llm_client` / `llm_model`, captioning `office_notice.png` via Gemini's OpenAI-compatible endpoint |
| 07 | [plugins_and_custom_converters](02_intermediate/07_plugins_and_custom_converters/) | `DocumentConverter`, `register_converter()`, writing a converter for a synthetic format |
| 08 | [stream_info_and_format_hints](02_intermediate/08_stream_info_and_format_hints/) | `StreamInfo`, `file_extension` hints, and how a wrong hint silently degrades output |
| 09 | [intermediate_checkpoint_project](02_intermediate/09_intermediate_checkpoint_project/) | **Checkpoint:** a "drop folder" converter combining a custom converter with graceful failure handling |

## Advanced: production integration and comparison

| # | Lesson | Concept |
|---|--------|---------|
| 10 | [feeding_markitdown_into_llamaindex](03_advanced/10_feeding_markitdown_into_llamaindex/) | Converting fixtures into `llama_index.core.Document`, building and querying a `VectorStoreIndex` |
| 11 | [comparing_markitdown_and_liteparse](03_advanced/11_comparing_markitdown_and_liteparse/) | The same PDF fixture through both MarkItDown and LiteParse, side by side, timed |
| 12 | [advanced_capstone_project](03_advanced/12_advanced_capstone_project/) | **Capstone:** one Gemini-backed searchable index over the full mixed `fixtures/` folder, including a captioned image |
