"""Lesson 5: reading structure, headings, sections, and plain text.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/docling/01_beginner/05_reading_structure/lesson.py
"""

from pathlib import Path

from docling.document_converter import DocumentConverter
from docling_core.types.doc import DocItemLabel

SAMPLE_DATA = Path(__file__).parent.parent.parent / "sample_data"


def main() -> None:
    converter = DocumentConverter()
    result = converter.convert(SAMPLE_DATA / "project_plan.docx")
    doc = result.document

    # Filtering doc.texts by .label picks out just the headings,
    # ignoring body paragraphs and list items entirely. This is the
    # kind of thing that requires real parsing on a plain-text export,
    # here it's a one-line filter over structured items.
    headings = [t for t in doc.texts if t.label in (DocItemLabel.TITLE, DocItemLabel.SECTION_HEADER)]
    print("Document outline:")
    for heading in headings:
        print(f"  {heading.label}: {heading.text}")

    print()

    # export_to_text() is export_to_markdown()'s plainer sibling: no
    # #, no |, just the reading-order text. Useful when downstream code
    # (an older search index, a plain-text log) can't handle Markdown
    # syntax at all.
    plain = doc.export_to_text()
    print("export_to_text() output:")
    print(plain)


if __name__ == "__main__":
    main()
