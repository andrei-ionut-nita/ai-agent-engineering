"""Lesson 12: exporting to JSON and loading it back.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/docling/02_intermediate/12_exporting_to_json/lesson.py
"""

import json
from pathlib import Path

from docling.document_converter import DocumentConverter
from docling_core.types.doc.document import DoclingDocument

SAMPLE_DATA = Path(__file__).parent.parent.parent / "sample_data"
OUTPUT_PATH = Path(__file__).parent / "quarterly_report.docling.json"


def main() -> None:
    converter = DocumentConverter()
    result = converter.convert(SAMPLE_DATA / "quarterly_report.pdf")
    doc = result.document

    # export_to_dict() is the full, lossless structure behind every
    # export_to_*() call so far, texts, tables, pictures, groups, and
    # provenance (which page, which bounding box), as plain Python
    # dicts and lists. This is what you'd persist if you wanted to
    # re-render a document later without re-running the whole pipeline.
    as_dict = doc.export_to_dict()
    print(f"Top-level keys: {sorted(as_dict.keys())}")
    print(f"Schema: {as_dict['schema_name']} v{as_dict['version']}")

    OUTPUT_PATH.write_text(json.dumps(as_dict, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.stat().st_size:,} bytes to {OUTPUT_PATH.name}")
    print()

    # The dict round-trips back into a real DoclingDocument, with every
    # method (export_to_markdown(), tables, pictures) working exactly as
    # it did on the freshly converted object. This is what makes the
    # JSON export useful for a real pipeline: convert once, cache the
    # JSON, reload and re-export to Markdown or a DataFrame later
    # without ever touching the layout or table models again.
    reloaded = DoclingDocument.model_validate(as_dict)
    print(f"Reloaded document: {len(reloaded.texts)} texts, {len(reloaded.tables)} tables")
    print(f"Original document:  {len(doc.texts)} texts, {len(doc.tables)} tables")
    print()
    print("Reloaded document's markdown export (first 100 chars):")
    print(reloaded.export_to_markdown()[:100])


if __name__ == "__main__":
    main()
