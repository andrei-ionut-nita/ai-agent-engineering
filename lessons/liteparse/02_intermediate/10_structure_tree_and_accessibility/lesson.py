"""
Lesson 10: extract_structure_tree, StructureTree, and what "tagged PDF"
means for accessibility.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/liteparse/02_intermediate/10_structure_tree_and_accessibility/lesson.py

A "tagged PDF" carries a second, hidden document inside it: a logical
structure tree that says "this run of text is a heading," "this is a
paragraph," "this is a table," independent of how it's drawn on the
page. This is what screen readers rely on to read a PDF aloud in a
sensible order, and it's also useful for anyone (or any parser) that
wants a document's structure without guessing at it from layout alone.
"""

import liteparse

SAMPLE_PDF = "lessons/liteparse/sample_data/employee_handbook.pdf"


def describe(element, depth: int = 0) -> None:
    indent = "  " * depth
    label = f"{indent}<{element.type}>"
    if element.actual_text:
        label += f" actual_text={element.actual_text!r}"
    print(label)
    for child in element.children:
        describe(child, depth + 1)


def main() -> None:
    # extract_structure_tree=True populates page.structure_tree with
    # whatever tagged structure the PDF actually contains. Not every
    # PDF has one: tagging is opt-in when a PDF is authored (LibreOffice
    # added it automatically when these sample PDFs were exported).
    parser = liteparse.LiteParse(ocr_enabled=False, quiet=True, extract_structure_tree=True)
    result = parser.parse(SAMPLE_PDF)

    tree = result.pages[0].structure_tree
    print(f"{SAMPLE_PDF} structure tree: {len(tree.roots)} root element(s)\n")

    for root in tree.roots:
        # Each StructureTreeElement has a tag (type), like "Document",
        # "P" (paragraph), "H1", or "Table", plus optional accessibility
        # fields (alt_text for images, actual_text as a screen-reader
        # override), and children forming a real tree, mirroring the
        # logical structure of the document, not its visual layout.
        describe(root)

    # Why this matters beyond accessibility: a well-tagged PDF's
    # structure tree gives you ground-truth "this is a heading, this is
    # a table, this is a list" without inferring it from font size or
    # position. A screen reader uses exactly this tree to read the
    # document in logical order; a document-processing pipeline can use
    # the same tree to chunk text by real structural boundaries instead
    # of guessing from whitespace.
    paragraph_count = sum(1 for root in tree.roots for child in root.children if child.type == "P")
    print(f"\n{paragraph_count} tagged <P> (paragraph) element(s) found under the root")


if __name__ == "__main__":
    main()
