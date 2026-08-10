"""
Lesson 6: extract_form_fields=True and FormField.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/liteparse/02_intermediate/06_tables_and_form_fields/lesson.py

sample_data/intake_form.pdf is a real AcroForm PDF: text fields, radio
buttons, and a checkbox, built as actual fillable form widgets, not just
text that looks like a form. This lesson extracts those widgets as
structured data instead of flat text.
"""

import liteparse

SAMPLE_PDF = "lessons/liteparse/sample_data/intake_form.pdf"


def main() -> None:
    # extract_form_fields=True is the only thing needed to turn on form
    # extraction. It's off by default because most PDFs don't have
    # AcroForm fields at all, and walking the form widget tree has a
    # (small) cost you shouldn't pay unless you need it.
    parser = liteparse.LiteParse(ocr_enabled=False, quiet=True, extract_form_fields=True)
    result = parser.parse(SAMPLE_PDF)

    page = result.pages[0]

    # form_fields lives on the PAGE, not on the ParseResult, since form
    # widgets are placed on specific pages. It's None unless
    # extract_form_fields=True was set (contrast with text_items, which
    # is always populated).
    print(f"{SAMPLE_PDF}: {len(page.form_fields)} form field(s) found\n")

    for field in page.form_fields:
        # Every FormField has an id/name and a widget type: "text" for
        # a fillable text box, "radio" for one button in a radio group
        # (each button in the group is its own FormField, sharing the
        # same name, distinguished by control_index), "checkbox" for a
        # single toggle. value/checked reflect whatever the PDF shipped
        # with as a default, this form ships mostly blank except for
        # its pre-selected radio option and checkbox.
        print(f"  field: {field.name!r} (id={field.id!r})")
        print(f"    type: {field.type}, label: {field.alternate_name!r}")
        if field.type == "radio":
            print(f"    option {field.control_index}: checked={field.checked}, export_value={field.export_value!r}")
        elif field.type == "checkbox":
            print(f"    checked: {field.checked}, export_value={field.export_value!r}")
        else:
            print(f"    value: {field.value!r}")
        print()


if __name__ == "__main__":
    main()
