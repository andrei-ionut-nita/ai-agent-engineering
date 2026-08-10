# Lesson 11: chunking a `DoclingDocument` for RAG with `HybridChunker`

## Why not just split the Markdown string every N characters

A naive chunker that slices `export_to_markdown()`'s output every N
characters doesn't know where a table row ends or a section begins,
it will happily cut a table in half or split a sentence across two
chunks. `HybridChunker`, from `docling_core.transforms.chunker`,
starts from the `DoclingDocument`'s own structure instead of the
rendered string: it splits on real section and table boundaries first,
then respects a tokenizer's max token count as a hard limit, merging
small adjacent pieces under the same heading where they still fit.

## Chunking a document

```python
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker

chunker = HybridChunker()
chunks = list(chunker.chunk(dl_doc=doc))
```

Each `chunk` carries `.text` (the chunk's own content) and `.meta`,
which includes `.headings`, the section heading(s) that chunk falls
under. That's the same outline Lesson 5 pulled out by hand with a list
comprehension, `HybridChunker` tracks it automatically, per chunk, so
you always know which part of the document a retrieved chunk came
from.

## `contextualize()`

```python
contextualized = chunker.contextualize(chunk=chunk)
```

A chunk's raw `.text` for a table row might read like
`"North, Product Line = Hardware. North, Q2 Revenue = $412,000..."`,
correct, but thin on its own once it's embedded and sitting in a
vector store next to thousands of other chunks. `contextualize()`
prepends the chunk's heading(s), so the string that actually gets
embedded reads `"Revenue by Region\nNorth, Product Line = Hardware..."`,
carrying enough context to be found and understood on its own. This is
the string you should hand to an embedding model, not the bare
`.text`.

## Running it

```bash
uv run python lessons/docling/02_intermediate/11_chunking_with_hybridchunker/lesson.py
```

## Expected output

```
quarterly_report.pdf produced 3 chunks

--- chunk 0 (headings: ['Executive Summary']) ---
Revenue grew across all three regions this quarter, led by the North region's expansion into two new distribution partners. The table below breaks res
contextualized: Executive Summary
Revenue grew across all three regions this quarter, led by the North region's expansion into two new distribution partners. The tabl

--- chunk 1 (headings: ['Revenue by Region']) ---
North, Product Line = Hardware. North, Q2 Revenue = $412,000. North, Q3 Revenue = $498,000. North, Growth = +20.9%. North, Product Line = Services. No
contextualized: Revenue by Region
North, Product Line = Hardware. North, Q2 Revenue = $412,000. North, Q3 Revenue = $498,000. North, Growth = +20.9%. North, Product L

--- chunk 2 (headings: ['Outlook']) ---
Q4 guidance assumes the North region's new partners ramp to full volume by week six. Services revenue is expected to keep pace with hardware growth as
contextualized: Outlook
Q4 guidance assumes the North region's new partners ramp to full volume by week six. Services revenue is expected to keep pace with hardware g
```

Notice the table became its own chunk (chunk 1), and its rows were
serialized as `key = value` pairs rather than a pipe table, that
serialization is exactly what makes a table row searchable by an
embedding model, "North, Growth = +20.9%" is meaningful text on its
own in a way a raw pipe-table row fragment would not be.

## Checkpoint

- **`HybridChunker`**: splits on the document's own structure first, a
  tokenizer's max length second, never cutting a table row or heading
  mid-way.
- **`chunk.meta.headings`**: the section heading(s) each chunk belongs
  to, tracked automatically.
- **`contextualize(chunk)`**: prepends those headings to the chunk
  text, this is the string to actually embed, not the bare `.text`.
- **Table chunks are serialized as `key = value` pairs**: designed for
  embedding and retrieval, not for re-rendering as a table.

If anything here still feels unclear, ask before moving to Lesson 12.
