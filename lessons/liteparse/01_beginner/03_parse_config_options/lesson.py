"""
Lesson 3: configuring the parser, ocr_enabled, max_pages, target_pages,
dpi, output_format, and password.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/liteparse/01_beginner/03_parse_config_options/lesson.py

LiteParse() takes a long list of optional keyword arguments (this whole
course works through the important ones, tier by tier). This lesson
covers the handful you reach for immediately: turning OCR off when you
don't need it, limiting how many pages get parsed, choosing plain text
vs Markdown output, and unlocking a password-protected PDF.
"""

import liteparse

SAMPLE_PDF = "lessons/liteparse/sample_data/employee_handbook.pdf"


def main() -> None:
    # ocr_enabled=False: as Lesson 2 showed, LiteParse defaults to
    # ocr_enabled=True and can run OCR even on native-text pages if its
    # heuristics think it's worth trying. If you already know your
    # documents have a real text layer, turning OCR off skips that work
    # entirely, which is both faster and quieter (no OCR timing logs).
    fast_parser = liteparse.LiteParse(ocr_enabled=False, quiet=True)
    result = fast_parser.parse(SAMPLE_PDF)
    print(f"ocr_enabled=False: {len(result.text)} chars, {result.num_pages} page(s)")

    # max_pages caps how many pages get parsed at all, useful for a quick
    # preview of a huge document without paying to parse all of it.
    # target_pages instead selects specific pages by number, e.g. "1-5,10".
    # Both work against employee_handbook.pdf, which only has 1 page, so
    # the effect here is a no-op, but the option is what matters: on a
    # multi-page document, max_pages=1 would return just page 1.
    capped = liteparse.LiteParse(ocr_enabled=False, quiet=True, max_pages=1)
    capped_result = capped.parse(SAMPLE_PDF)
    print(f"max_pages=1: {capped_result.num_pages} page(s) returned")

    targeted = liteparse.LiteParse(ocr_enabled=False, quiet=True, target_pages="1")
    targeted_result = targeted.parse(SAMPLE_PDF)
    print(f"target_pages='1': {targeted_result.num_pages} page(s) returned")

    # output_format="markdown" asks LiteParse to also populate
    # result.pages[i].markdown, a Markdown rendering of that page (headings,
    # lists, code-fenced blocks where it detects them) alongside the plain
    # .text. Useful when the downstream consumer (an LLM prompt, a
    # Markdown renderer) benefits from structure instead of flat text.
    markdown_parser = liteparse.LiteParse(ocr_enabled=False, quiet=True, output_format="markdown")
    markdown_result = markdown_parser.parse("lessons/liteparse/sample_data/product_spec.pdf")
    print("\noutput_format='markdown', first 200 chars of result.pages[0].markdown:")
    print(markdown_result.pages[0].markdown[:200])

    # password unlocks an encrypted PDF before parsing. None of this
    # course's sample PDFs are encrypted, so passing one here has no
    # effect either way, it's simply ignored on a document that doesn't
    # need it. On a real password-protected PDF, parsing without the
    # right password raises liteparse.ParseError instead of returning
    # garbled or empty text.
    unlock_attempt = liteparse.LiteParse(ocr_enabled=False, quiet=True, password="not-actually-needed")
    unlock_result = unlock_attempt.parse(SAMPLE_PDF)
    print(f"\npassword=<ignored on an unencrypted PDF>: {len(unlock_result.text)} chars, no error")


if __name__ == "__main__":
    main()
