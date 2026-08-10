"""Lesson 14: formula and code enrichment options.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/docling/03_advanced/14_formula_and_code_enrichment/lesson.py
"""

from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import DocItemLabel

SAMPLE_DATA = Path(__file__).parent.parent.parent / "sample_data"


def main() -> None:
    # do_formula_enrichment runs a dedicated model over regions the
    # layout model classified as a formula, recovering LaTeX. do_code_enrichment
    # does the same for regions classified as code, recovering language
    # and cleaner formatting. Both are off by default: they add a real
    # model pass, worth paying for only on documents that actually
    # contain formulas or code.
    options = PdfPipelineOptions()
    options.do_formula_enrichment = True
    options.do_code_enrichment = True

    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
    )
    result = converter.convert(SAMPLE_DATA / "research_note.pdf")
    doc = result.document

    print("Detected items:")
    for item, _level in doc.iterate_items():
        label = getattr(item, "label", type(item).__name__)
        text = getattr(item, "text", "") or ""
        print(f"  {label}: {text[:70]}")

    formula_or_code = [
        item for item in doc.pictures if item.label in (DocItemLabel.FORMULA, DocItemLabel.CODE)
    ]
    print()
    print(f"Items classified specifically as formula or code: {len(formula_or_code)}")
    print(
        "This fixture is a reportlab-rendered PDF, not real LaTeX-typeset "
        "math or a syntax-highlighted code block, so the layout model may "
        "not classify its formula-like line as a 'formula' region the way "
        "it reliably would on a real research paper. See README.md for what "
        "this demonstrates and doesn't."
    )


if __name__ == "__main__":
    main()
