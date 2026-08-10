"""
Lesson 2: LiteParse(), .parse(path), and .text.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/liteparse/01_beginner/02_first_parse_call/lesson.py

This is the smallest possible real use of LiteParse: build a parser,
point it at a PDF, read the extracted text back out.
"""

import liteparse

SAMPLE_PDF = "lessons/liteparse/sample_data/product_spec.pdf"


def main() -> None:
    # LiteParse() takes many optional keyword arguments (this whole course
    # works through the important ones), but every one of them has a
    # sensible default. Called with no arguments at all, you get a parser
    # configured for the common case: extract native text, run OCR only
    # if a page genuinely looks like it needs it.
    parser = liteparse.LiteParse()

    # .parse() accepts a path (str or pathlib.Path) to a PDF on disk and
    # returns a ParseResult. This is a synchronous, local function call:
    # by the time it returns, parsing already happened, entirely on this
    # machine, no request in flight anywhere.
    result = parser.parse(SAMPLE_PDF)

    # .text is the flattened, whole-document text: every page's text
    # concatenated together in reading order. For most "I just need the
    # words in this PDF" use cases (feeding a search index, an LLM
    # prompt, a keyword filter), .text is the only field you need.
    print(f"\nParsed: {SAMPLE_PDF}")
    print(f"Character count: {len(result.text)}")
    print("\n--- result.text ---")
    print(result.text)


if __name__ == "__main__":
    main()
