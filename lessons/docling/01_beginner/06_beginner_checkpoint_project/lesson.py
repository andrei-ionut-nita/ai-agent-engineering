"""Lesson 6 (Beginner checkpoint): convert a whole folder to Markdown.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/docling/01_beginner/06_beginner_checkpoint_project/lesson.py

No new API. This proves Lessons 1-5 add up to something useful:
convert every sample document with one converter, one loop, and write
real .md files to disk, the actual shape of a folder-to-Markdown
ingestion script.
"""

from pathlib import Path

from docling.document_converter import DocumentConverter

SAMPLE_DATA = Path(__file__).parent.parent.parent / "sample_data"
OUTPUT_DIR = Path(__file__).parent / "converted"

# research_note.pdf and scanned_invoice.pdf are left for Lessons 9 and
# 14, this checkpoint sticks to the three formats covered so far: PDF,
# DOCX, PPTX, each with a native text layer.
SOURCE_FILES = ["quarterly_report.pdf", "project_plan.docx", "team_update.pptx"]


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    converter = DocumentConverter()

    summary = []
    for filename in SOURCE_FILES:
        source_path = SAMPLE_DATA / filename
        result = converter.convert(source_path)
        markdown = result.document.export_to_markdown()

        output_path = OUTPUT_DIR / f"{source_path.stem}.md"
        output_path.write_text(markdown, encoding="utf-8")

        summary.append(
            (
                filename,
                source_path.suffix,
                len(result.document.texts),
                len(result.document.tables),
                len(result.document.pictures),
            )
        )

    print(f"Converted {len(summary)} files from sample_data/ into {OUTPUT_DIR}\n")
    header = f"{'Source file':<24}{'Format':<10}{'Texts':<8}{'Tables':<8}{'Pictures':<8}"
    print(header)
    print("-" * len(header))
    for name, fmt, texts, tables, pictures in summary:
        print(f"{name:<24}{fmt:<10}{texts:<8}{tables:<8}{pictures:<8}")


if __name__ == "__main__":
    main()
