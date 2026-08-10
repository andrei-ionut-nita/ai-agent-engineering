"""Lesson 13 (Intermediate checkpoint): table + OCR + chunked JSON pipeline.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/docling/02_intermediate/13_intermediate_checkpoint_project/lesson.py

No new API. This combines Lessons 7-12 into one script: convert two
very different documents (a native-text PDF with a table, an
image-only scanned PDF) with default pipeline options, chunk each with
HybridChunker, and write everything out as one JSON file ready for an
embedding step.
"""

import json
from pathlib import Path

from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker

SAMPLE_DATA = Path(__file__).parent.parent.parent / "sample_data"
OUTPUT_PATH = Path(__file__).parent / "chunks.json"

# quarterly_report.pdf exercises the table pipeline (Lesson 8),
# scanned_invoice.pdf exercises OCR (Lesson 9). Default pipeline
# options handle both correctly with no per-file configuration, do_ocr
# and do_table_structure are both on by default.
SOURCE_FILES = ["quarterly_report.pdf", "scanned_invoice.pdf"]


def main() -> None:
    converter = DocumentConverter()
    chunker = HybridChunker()

    all_chunks = []
    for filename in SOURCE_FILES:
        result = converter.convert(SAMPLE_DATA / filename)
        doc = result.document

        for chunk in chunker.chunk(dl_doc=doc):
            all_chunks.append(
                {
                    "source": filename,
                    "headings": chunk.meta.headings,
                    "text": chunk.text,
                    "contextualized_text": chunker.contextualize(chunk=chunk),
                }
            )

    OUTPUT_PATH.write_text(json.dumps(all_chunks, indent=2), encoding="utf-8")

    print(f"Converted {len(SOURCE_FILES)} documents into {len(all_chunks)} chunks")
    print(f"Wrote {OUTPUT_PATH.name} ({OUTPUT_PATH.stat().st_size:,} bytes)\n")

    for entry in all_chunks:
        print(f"[{entry['source']}] {entry['headings']}")
        print(f"  {entry['contextualized_text'][:100]}")


if __name__ == "__main__":
    main()
