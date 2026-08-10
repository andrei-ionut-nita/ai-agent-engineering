"""
Lesson 8: OCR for scanned documents, the ocr_enabled contrast.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/liteparse/02_intermediate/08_ocr_for_scanned_documents/lesson.py

sample_data/scanned_notice.pdf is a genuinely scanned document: it was
built by rendering a PNG image into a PDF, so it has no PDF text
objects at all, just a picture of text. This lesson parses it twice,
once with OCR off and once with OCR on, and shows the difference
directly, this is the contrast every earlier lesson has been pointing
toward.
"""

import liteparse

SCANNED_PDF = "lessons/liteparse/sample_data/scanned_notice.pdf"


def main() -> None:
    # ocr_enabled=False: LiteParse only ever looks at the PDF's native
    # text objects. A scanned page (a picture of a document) has none,
    # so there is nothing to extract, no matter how much readable text
    # a human looking at the page would see.
    no_ocr = liteparse.LiteParse(ocr_enabled=False, quiet=True)
    no_ocr_result = no_ocr.parse(SCANNED_PDF)
    print("ocr_enabled=False:")
    print(f"  characters extracted: {len(no_ocr_result.text)}")
    print(f"  text: {no_ocr_result.text!r}")

    # ocr_enabled=True (the default): LiteParse's complexity heuristics
    # detect that this page has no usable native text and a full-page
    # image (exactly the "scanned" signature), renders the page to a
    # bitmap, and runs Tesseract OCR against it to recover text.
    with_ocr = liteparse.LiteParse(ocr_enabled=True, quiet=True)
    with_ocr_result = with_ocr.parse(SCANNED_PDF)
    print("\nocr_enabled=True:")
    print(f"  characters extracted: {len(with_ocr_result.text)}")
    print(f"  text: {with_ocr_result.text!r}")

    # is_complex() exposes the same signals LiteParse's own OCR decision
    # is based on, without running a full parse. needs_ocr and reasons
    # explain in plain terms why this page needed OCR at all.
    stats = with_ocr.is_complex(SCANNED_PDF)
    page_stats = stats[0]
    print(f"\nis_complex() verdict for page {page_stats.page_number}:")
    print(f"  needs_ocr: {page_stats.needs_ocr}")
    print(f"  reasons: {page_stats.reasons}")
    print(f"  text_length (native): {page_stats.text_length}")
    print(f"  full_page_image: {page_stats.full_page_image}")


if __name__ == "__main__":
    main()
