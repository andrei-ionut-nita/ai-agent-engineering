"""Lesson 7: PdfPipelineOptions and format_options.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/docling/02_intermediate/07_pdf_pipeline_options/lesson.py
"""

import time
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

SAMPLE_DATA = Path(__file__).parent.parent.parent / "sample_data"


def main() -> None:
    pdf_path = SAMPLE_DATA / "quarterly_report.pdf"

    # A default DocumentConverter is equivalent to explicitly passing
    # PdfPipelineOptions() with its own defaults, do_ocr=True,
    # do_table_structure=True. Run it first so its model weights are
    # loaded and warm, the fast comparison below then measures only the
    # options' effect on per-page work, not one-time model load cost.
    default_converter = DocumentConverter()
    start = time.perf_counter()
    default_result = default_converter.convert(pdf_path)
    default_seconds = time.perf_counter() - start

    print(f"Default pipeline options: {default_seconds:.2f}s")
    print(f"  tables detected: {len(default_result.document.tables)}")
    print()

    # Turning OCR and table structure recognition off skips the two
    # most expensive per-page models. On a PDF that already has a real
    # text layer (this one does), do_ocr=False loses nothing, the text
    # layer is read directly either way.
    fast_options = PdfPipelineOptions()
    fast_options.do_ocr = False
    fast_options.do_table_structure = False

    fast_converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=fast_options)}
    )

    start = time.perf_counter()
    fast_result = fast_converter.convert(pdf_path)
    fast_seconds = time.perf_counter() - start

    print(f"do_ocr=False, do_table_structure=False: {fast_seconds:.2f}s")
    print(f"  tables detected: {len(fast_result.document.tables)}")
    print(
        "  (a table item is still emitted from the PDF's own cell grid, "
        "just without TableFormer's structure model reconciling merged "
        "cells and headers)"
    )


if __name__ == "__main__":
    main()
