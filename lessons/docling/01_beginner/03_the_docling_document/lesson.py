"""Lesson 3: what's actually inside a DoclingDocument.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/docling/01_beginner/03_the_docling_document/lesson.py
"""

from pathlib import Path

from docling.document_converter import DocumentConverter

SAMPLE_DATA = Path(__file__).parent.parent.parent / "sample_data"


def main() -> None:
    converter = DocumentConverter()
    result = converter.convert(SAMPLE_DATA / "quarterly_report.pdf")
    doc = result.document

    # export_to_markdown() hides the structure behind a string. These
    # attributes are that structure, directly: separate lists for text
    # items, tables, and pictures, each a real object, not text you'd
    # have to re-parse.
    print(f"Text items:  {len(doc.texts)}")
    print(f"Tables:      {len(doc.tables)}")
    print(f"Pictures:    {len(doc.pictures)}")
    print()

    # iterate_items() walks the document in reading order, yielding
    # every item alongside its nesting level, this is how docling
    # itself builds export_to_markdown() under the hood.
    print("Reading order (label: text preview):")
    for item, _level in doc.iterate_items():
        label = getattr(item, "label", type(item).__name__)
        text = getattr(item, "text", "")
        preview = f": {text[:60]}" if text else ""
        print(f"  {label}{preview}")


if __name__ == "__main__":
    main()
