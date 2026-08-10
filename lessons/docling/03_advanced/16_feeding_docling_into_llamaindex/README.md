# Lesson 16: feeding docling's chunks into LlamaIndex

## Where docling's job ends and LlamaIndex's begins

Lesson 11 chunked a `DoclingDocument` with `HybridChunker` and printed
the chunks. This lesson is the natural next step: hand those chunks to
[llamaindex](../../../llamaindex/) and build something queryable. The
integration is small on purpose, docling's job ends at producing
structured, contextualized chunk text, LlamaIndex's job starts at
accepting `Document` objects, neither library needs to know the other
exists.

```python
documents = []
for filename in SOURCE_FILES:
    result = converter.convert(SAMPLE_DATA / filename)
    for chunk in chunker.chunk(dl_doc=result.document):
        documents.append(
            Document(
                text=chunker.contextualize(chunk=chunk),
                metadata={"source": filename, "headings": chunk.meta.headings},
            )
        )
```

One `Document` per docling chunk, not one per file. This matters:
LlamaIndex's own default ingestion would re-split whole-file text with
its own splitter, which knows nothing about docling's table and
section boundaries. Chunking with `HybridChunker` first, before
LlamaIndex ever sees the text, means retrieval granularity respects
the structure docling already found, not a generic character-count
split.

## From there, it's the standard LlamaIndex loop

```python
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query(question)
```

This is exactly [`lessons/llamaindex/`](../../../llamaindex/)'s core
pattern from its own beginner lessons (`Settings`, `Document`,
`VectorStoreIndex`, query engines), see that course for what each
piece means in depth. By this point the index has no idea its input
text came from a PDF table row versus a DOCX paragraph, it's just text
with metadata.

## Setup

This lesson needs a `GOOGLE_API_KEY` in `.env` at the project root,
the same key used throughout `lessons/llamaindex/`, and makes real
API calls (embeddings to build the index, generation to answer each
query), keep that in mind against a constrained quota.

## Running it

```bash
uv run python lessons/docling/03_advanced/16_feeding_docling_into_llamaindex/lesson.py
```

## Expected output

Exact wording will vary slightly (it's a real LLM call), the facts
should match:

```
Converted 3 fixtures into 10 LlamaIndex Documents.

Q: How much did North region hardware revenue grow in Q3?
A: The North region hardware revenue grew by +20.9% in Q3.

Q: What is the main risk in the warehouse automation rollout?
A: The main risk is the parts lead time, specifically because conveyor motors currently have an eight-week order-to-delivery window.
```

## Checkpoint

- **Docling's role stops at producing chunk text**: LlamaIndex has no
  awareness of docling, or of PDFs, DOCX, or PPTX at all.
- **One `Document` per docling chunk, not per file**: keeps LlamaIndex's
  retrieval granularity aligned with docling's structural chunk
  boundaries, not a generic re-split.
- **`chunker.contextualize(chunk)` as the embedded text**: the same
  choice made in Lesson 11, carried through into what actually gets
  embedded here.

If anything here still feels unclear, ask before moving to Lesson 17.
