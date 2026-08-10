"""Lesson 4: one converter, many formats.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/docling/01_beginner/04_converting_docx_and_pptx/lesson.py
"""

from pathlib import Path

from docling.document_converter import DocumentConverter

SAMPLE_DATA = Path(__file__).parent.parent.parent / "sample_data"


def main() -> None:
    # The exact same DocumentConverter instance handles PDF, DOCX, and
    # PPTX, no per-format setup, no separate converter objects. Docling
    # picks the right backend from the file extension (or content, for
    # a stream) automatically.
    converter = DocumentConverter()

    for filename in ["quarterly_report.pdf", "project_plan.docx", "team_update.pptx"]:
        result = converter.convert(SAMPLE_DATA / filename)
        doc = result.document
        markdown = doc.export_to_markdown()
        first_line = markdown.strip().splitlines()[0]

        print(f"{filename}")
        print(f"  format: {result.input.format}")
        print(f"  texts={len(doc.texts)} tables={len(doc.tables)} pictures={len(doc.pictures)}")
        print(f"  first line: {first_line}")
        print()


if __name__ == "__main__":
    main()
