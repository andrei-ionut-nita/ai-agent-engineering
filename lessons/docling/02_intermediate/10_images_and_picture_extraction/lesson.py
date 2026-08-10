"""Lesson 10: extracting pictures as real image files.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/docling/02_intermediate/10_images_and_picture_extraction/lesson.py
"""

from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

SAMPLE_DATA = Path(__file__).parent.parent.parent / "sample_data"
OUTPUT_DIR = Path(__file__).parent / "extracted_images"


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    # export_to_markdown() only ever produced an "<!-- image -->"
    # placeholder for the chart in quarterly_report.pdf (see Lesson 3),
    # the picture itself was detected but never rendered out. These two
    # options change that: generate_picture_images renders each detected
    # picture region as an actual raster image, images_scale controls
    # the resolution it's rendered at relative to the PDF page.
    options = PdfPipelineOptions()
    options.generate_picture_images = True
    options.images_scale = 2.0

    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
    )
    result = converter.convert(SAMPLE_DATA / "quarterly_report.pdf")
    doc = result.document

    print(f"Pictures detected: {len(doc.pictures)}")

    for i, picture in enumerate(doc.pictures):
        # get_image(doc) returns a PIL Image, rendered from the page at
        # the picture's exact bounding box, this is the actual figure,
        # not a screenshot of the whole page.
        image = picture.get_image(doc)
        if image is None:
            print(f"  picture {i}: no image available")
            continue

        output_path = OUTPUT_DIR / f"picture_{i}.png"
        image.save(output_path)
        print(f"  picture {i}: {image.size[0]}x{image.size[1]} px -> {output_path.name}")


if __name__ == "__main__":
    main()
