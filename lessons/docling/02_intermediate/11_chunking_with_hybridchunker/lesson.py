"""Lesson 11: chunking a DoclingDocument for RAG with HybridChunker.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/docling/02_intermediate/11_chunking_with_hybridchunker/lesson.py
"""

from pathlib import Path

from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker

SAMPLE_DATA = Path(__file__).parent.parent.parent / "sample_data"


def main() -> None:
    converter = DocumentConverter()
    result = converter.convert(SAMPLE_DATA / "quarterly_report.pdf")
    doc = result.document

    # HybridChunker is layout-aware: it splits on the document's own
    # structure (section boundaries, table boundaries) first, then
    # respects a tokenizer's max token count as a hard limit, merging
    # small adjacent chunks under the same heading where it fits. This
    # is deliberately not a naive "every N characters" splitter, a chunk
    # never cuts a table row in half.
    chunker = HybridChunker()
    chunks = list(chunker.chunk(dl_doc=doc))

    print(f"quarterly_report.pdf produced {len(chunks)} chunks\n")

    for i, chunk in enumerate(chunks):
        # chunk.meta.headings carries the section heading(s) each chunk
        # falls under, exactly the outline Lesson 5 pulled out by hand,
        # HybridChunker tracks it automatically per chunk.
        headings = chunk.meta.headings
        print(f"--- chunk {i} (headings: {headings}) ---")
        print(chunk.text[:150])

        # contextualize() prepends those headings to the chunk text,
        # this is the string you'd actually embed: a chunk that reads
        # "Revenue by Region\nNorth, Product Line = Hardware..." carries
        # far more retrievable meaning on its own than the bare row text.
        contextualized = chunker.contextualize(chunk=chunk)
        print(f"contextualized: {contextualized[:150]}")
        print()


if __name__ == "__main__":
    main()
