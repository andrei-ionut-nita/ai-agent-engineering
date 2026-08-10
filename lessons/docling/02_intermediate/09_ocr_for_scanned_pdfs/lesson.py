"""Lesson 9: OCR for scanned, image-only PDFs.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/docling/02_intermediate/09_ocr_for_scanned_pdfs/lesson.py
"""

from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

SAMPLE_DATA = Path(__file__).parent.parent.parent / "sample_data"


def main() -> None:
    # scanned_invoice.pdf is a picture of an invoice saved as a PDF, the
    # same shape a phone-camera or flatbed scan produces: no text layer
    # at all, only pixels. Every earlier lesson's PDFs had a real text
    # layer, this one does not, so it's the fixture that actually needs
    # OCR to produce anything.
    scanned_pdf = SAMPLE_DATA / "scanned_invoice.pdf"

    # do_ocr=False here isn't a speed optimization like Lesson 7, it's a
    # deliberate demonstration of the failure mode: with no text layer
    # and no OCR, there is nothing to extract.
    no_ocr_options = PdfPipelineOptions()
    no_ocr_options.do_ocr = False
    no_ocr_converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=no_ocr_options)}
    )
    no_ocr_result = no_ocr_converter.convert(scanned_pdf)
    no_ocr_text = no_ocr_result.document.export_to_text()

    print(f"do_ocr=False: extracted {len(no_ocr_text)} characters")
    print()

    # do_ocr=True is the default (every earlier lesson used it without
    # knowing), it runs docling's default OCR engine over the page image
    # and inserts the recognized text back into the document structure.
    ocr_converter = DocumentConverter()
    ocr_result = ocr_converter.convert(scanned_pdf)
    ocr_text = ocr_result.document.export_to_text()

    print(f"do_ocr=True (default): extracted {len(ocr_text)} characters")
    print()
    print(ocr_text)


if __name__ == "__main__":
    main()
