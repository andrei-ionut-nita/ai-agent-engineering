# Lesson 18 (Advanced capstone): folder to queryable RAG index

## Everything this course covered, in one script

This capstone introduces no new docling or LlamaIndex API. It combines
pieces already built across the whole course:

- **Lesson 15**: one reused `DocumentConverter`, driven over a whole
  folder.
- **Lesson 9**: OCR, needed for `scanned_invoice.pdf`'s missing text
  layer.
- **Lesson 8**: table structure recognition, needed for
  `quarterly_report.pdf`'s table.
- **Lesson 11**: `HybridChunker`, structure-aware chunking instead of a
  naive character split.
- **Lesson 16**: the docling-chunk-to-LlamaIndex-`Document` handoff,
  and the `VectorStoreIndex` -> query engine loop.

The difference from Lesson 16 is scope: every file in `sample_data/`,
five documents across four formats (a native-text PDF with a table, an
image-only scanned PDF, a DOCX, a PPTX), one converter, one chunker,
one index.

## Proving the index actually spans every format

Four questions, each answerable from a different source file, confirm
the index isn't secretly only working off the easiest file to convert:

| Question | Answer lives in |
|---|---|
| North region hardware revenue growth | `quarterly_report.pdf`, via TableFormer |
| Main risk in the warehouse rollout | `project_plan.docx` |
| Mitigation for the conveyor motor risk | `team_update.pptx` |
| Total due on invoice 4471 | `scanned_invoice.pdf`, via OCR, no text layer to begin with |

If the retrieved source for each answer matches the format in that
table, the whole pipeline, four formats in (five files, since
`research_note.pdf` is converted too but not directly queried here),
one Gemini-backed index, worked end to end.

## The code, piece by piece

```python
source_files = sorted(p for p in SAMPLE_DATA.iterdir() if p.is_file())
for source_path in source_files:
    result = converter.convert(source_path)
    for chunk in chunker.chunk(dl_doc=result.document):
        documents.append(
            Document(text=chunker.contextualize(chunk=chunk), metadata={"source": source_path.name})
        )
```

No format-specific branching, no skip list, the same default
`DocumentConverter` and `HybridChunker` handle a table-bearing PDF, a
scanned PDF, a DOCX, and a PPTX identically. `response.source_nodes`
on the query result carries back each retrieved chunk's `metadata`, so
printing `top_sources` per answer is a direct check that retrieval
actually pulled from the right file, not a lucky guess.

## Setup

Needs a `GOOGLE_API_KEY` in `.env` at the project root, and makes real
API calls (embeddings for indexing, generation for each answer), keep
that in mind against a constrained quota.

## Running it

```bash
uv run python lessons/docling/03_advanced/18_advanced_capstone_project/lesson.py
```

## Expected output

Exact wording varies slightly (real LLM calls), retrieved sources
should match:

```
Converted 5 files into 13 chunks.

Q: How much did North region hardware revenue grow in Q3?
A: North region hardware revenue grew by 20.9% in Q3, with revenue increasing from $412,000 in Q2 to $498,000 in Q3.
   (expected source: quarterly_report.pdf, retrieved from: ['quarterly_report.pdf'])

Q: What is the main risk in the warehouse automation rollout?
A: The main risk is parts lead time, specifically because conveyor motors currently have an eight-week order-to-delivery window.
   (expected source: project_plan.docx, retrieved from: ['project_plan.docx', 'team_update.pptx'])

Q: What is the mitigation plan for the conveyor motor lead time risk?
A: The mitigation plan is to order the South and West motors now.
   (expected source: team_update.pptx, retrieved from: ['project_plan.docx', 'team_update.pptx'])

Q: What is the total due on invoice 4471?
A: The total due on invoice 4471 is $5,927.80.
   (expected source: scanned_invoice.pdf (via OCR), retrieved from: ['quarterly_report.pdf', 'scanned_invoice.pdf'])
```

Two of the four questions retrieved chunks from a second, related file
alongside the expected one, that's normal for vector retrieval on a
small corpus (the risk and mitigation questions are topically close),
not a failure, the answer text itself is still correct and traceable
back to the right source.

## Where to go from here

This capstone stops at a script that answers four hardcoded questions.
A real next step would wrap `build_index()` in a small FastAPI service
(the same shape as [pgvector](../../../pgvector/)'s capstone), swap
the in-memory `VectorStoreIndex` for a persistent store so the index
survives a restart, and add new documents incrementally instead of
rebuilding from scratch on every run. Nothing about the docling side
of this pipeline would need to change, docling's job already ends at
producing well-structured, contextualized chunks, everything past that
point is ordinary RAG infrastructure work covered in
[pgvector](../../../pgvector/) and [langgraph](../../../langgraph/).

Congratulations on completing the course.
