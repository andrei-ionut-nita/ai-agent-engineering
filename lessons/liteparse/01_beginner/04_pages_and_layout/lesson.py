"""
Lesson 4: result.pages, and per-page layout with ParsedPage.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/liteparse/01_beginner/04_pages_and_layout/lesson.py

Lesson 2 used result.text, the whole document flattened into one string.
This lesson looks at result.pages, the list of ParsedPage objects that
.text is actually built from, which is what you need whenever "which
page did this come from" matters.
"""

import liteparse

SAMPLE_PDF = "lessons/liteparse/sample_data/employee_handbook.pdf"


def main() -> None:
    parser = liteparse.LiteParse(ocr_enabled=False, quiet=True)
    result = parser.parse(SAMPLE_PDF)

    # result.pages is a list of ParsedPage, one per page, in order.
    # result.num_pages is just len(result.pages), a convenience property.
    print(f"{SAMPLE_PDF}: {result.num_pages} page(s)")

    for page in result.pages:
        # Each ParsedPage carries its own page_num (1-indexed), the
        # page's physical size in points (72 points per inch, so
        # 595 x 842 is a standard A4 page), and that page's own slice
        # of text, independent of every other page.
        print(f"\n--- page {page.page_num} ---")
        print(f"  size: {page.width:.0f} x {page.height:.0f} points")
        print(f"  text length: {len(page.text)} characters")

        # text_items is the finer-grained layer underneath .text: one
        # TextItem per run of text LiteParse found on the page, each
        # with its own bounding box (x, y, width, height, in the same
        # point units as the page size) and font info. .text is built
        # by joining these in reading order; text_items is what you'd
        # reach for if you needed to know WHERE on the page a piece of
        # text sits, not just that it exists.
        print(f"  text items: {len(page.text_items)}")
        first_item = page.text_items[0]
        print(
            f"  first item: {first_item.text!r} at "
            f"(x={first_item.x:.1f}, y={first_item.y:.1f}), "
            f"font={first_item.font_name}, size={first_item.font_size}"
        )

    # get_page() looks up a page by its 1-indexed page_num, an
    # alternative to indexing result.pages directly (which is 0-indexed
    # like any Python list). Returns None if that page number doesn't exist.
    page_one = result.get_page(1)
    print(f"\nresult.get_page(1) found page_num={page_one.page_num}: {page_one is not None}")
    missing = result.get_page(99)
    print(f"result.get_page(99): {missing}")


if __name__ == "__main__":
    main()
