"""
Lesson 3: converting office documents (docx, pptx, xlsx).

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/markitdown/01_beginner/03_converting_office_documents/lesson.py

Lesson 2 converted a plain text file, where "conversion" barely means
anything, text goes in, the same text comes out. This lesson converts
three real office formats and looks at how each one's structure
(paragraphs, slides, cell grids) gets translated into Markdown.
"""

from pathlib import Path

from markitdown import MarkItDown

FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"


def show(md: MarkItDown, filename: str, note: str) -> None:
    result = md.convert(FIXTURES_DIR / filename)
    print(f"=== {filename} ===")
    print(f"({note})\n")
    print(result.markdown)
    print()


def main() -> None:
    md = MarkItDown()

    # .docx: a Word memo. Paragraphs become plain text lines. Whether a
    # paragraph becomes a Markdown '#' heading depends on whether it was
    # written with one of Word's built-in heading styles, plain bold text
    # doesn't count, only actual "Heading 1"/"Heading 2" styles do. This
    # fixture's section labels ("Summary", "What Is Covered") were typed as
    # plain bold text, not styled headings, so they come through as
    # ordinary paragraph text rather than '#' headings, worth noticing since
    # it's an easy assumption to get wrong.
    show(
        md,
        "remote_work_memo.docx",
        "Word paragraphs -> Markdown text lines (only real heading-styled text becomes '#')",
    )

    # .pptx: a slide deck. Each slide becomes a section marked with an
    # HTML comment ("<!-- Slide number: N -->"), since Markdown has no
    # native concept of "slide", followed by the slide's title (as a
    # heading) and its bullet points (as a list).
    show(
        md,
        "onboarding_deck.pptx",
        "Each slide -> a '<!-- Slide number: N -->' marker + heading + bullet list",
    )

    # .xlsx: a spreadsheet. Each sheet's data becomes a Markdown pipe
    # table, the header row becomes the table header, exactly the kind of
    # structure an LLM can read directly, no need to reconstruct a grid
    # from tab-separated values.
    show(
        md,
        "expense_report.xlsx",
        "Spreadsheet rows/columns -> a Markdown pipe table",
    )


if __name__ == "__main__":
    main()
