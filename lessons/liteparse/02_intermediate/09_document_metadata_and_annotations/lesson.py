"""
Lesson 9: extract_document_metadata, DocumentMetadata, extract_annotations,
and extract_links.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/liteparse/02_intermediate/09_document_metadata_and_annotations/lesson.py

sample_data/vendor_memo.pdf contains a real hyperlink annotation (a link
to a procurement policy). This lesson pulls it out as structured data,
alongside document-level provenance metadata that has nothing to do
with the page content at all.
"""

import liteparse

SAMPLE_PDF = "lessons/liteparse/sample_data/vendor_memo.pdf"


def main() -> None:
    # extract_document_metadata=True populates result.doc_meta, a
    # DocumentMetadata with provenance signals about the FILE itself,
    # not its content: when it was created, what PDF version it is,
    # whether it's encrypted, its raw file size. This comes from
    # PDFium and the PDF's own /Info dictionary, not from LiteParse
    # reading the page text.
    parser = liteparse.LiteParse(
        ocr_enabled=False,
        quiet=True,
        extract_document_metadata=True,
        extract_annotations=True,
        extract_links=True,
    )
    result = parser.parse(SAMPLE_PDF)

    print("Document metadata (result.doc_meta):")
    meta = result.doc_meta
    print(f"  creation_date: {meta.creation_date}")
    print(f"  file_version: {meta.file_version} (14 would mean PDF 1.4)")
    print(f"  is_encrypted: {meta.is_encrypted}")
    print(f"  raw_file_size: {meta.raw_file_size} bytes")
    print(f"  creator: {result.creator!r}")
    print(f"  producer: {result.producer!r}")

    # extract_annotations=True populates page.annotations: PDF
    # annotation objects (links, comments, highlights, stamps) that sit
    # ON TOP of the page content rather than being part of the text flow.
    page = result.pages[0]
    print(f"\nAnnotations on page 1 ({len(page.annotations)} found):")
    for annotation in page.annotations:
        print(f"  subtype: {annotation.subtype}")
        if annotation.uri:
            print(f"  uri: {annotation.uri}")
        print(f"  rect: x={annotation.rect.x:.0f}, y={annotation.rect.y:.0f}, "
              f"w={annotation.rect.width:.0f}, h={annotation.rect.height:.0f}")

    # extract_links=True (on by default) controls whether hyperlinks get
    # rendered as Markdown [text](url) syntax when output_format="markdown".
    # It's independent of extract_annotations: annotations give you the
    # link as structured data with a rect and URI; extract_links controls
    # how it's INLINED into text/markdown output.
    print(f"\nresult.text still reads as plain prose, the link text is inline:")
    print(f"  {result.text!r}")


if __name__ == "__main__":
    main()
