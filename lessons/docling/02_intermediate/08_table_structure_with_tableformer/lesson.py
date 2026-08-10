"""Lesson 8: table structure recognition with TableFormer.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/docling/02_intermediate/08_table_structure_with_tableformer/lesson.py
"""

from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.document_converter import DocumentConverter, PdfFormatOption

SAMPLE_DATA = Path(__file__).parent.parent.parent / "sample_data"


def convert_with_mode(mode: TableFormerMode):
    options = PdfPipelineOptions()
    options.table_structure_options.mode = mode
    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
    )
    return converter.convert(SAMPLE_DATA / "quarterly_report.pdf")


def main() -> None:
    # ACCURATE is the default, used implicitly in every earlier lesson.
    # FAST trades some structure accuracy for speed, useful when a
    # pipeline is converting a large batch of simple tables.
    result = convert_with_mode(TableFormerMode.ACCURATE)
    table = result.document.tables[0]

    # export_to_dataframe() is table-specific: a pandas DataFrame with
    # real rows and columns, the structured payoff of TableFormer having
    # actually understood the grid, not just a Markdown string you'd
    # have to re-parse to get individual cell values back.
    df = table.export_to_dataframe(result.document)
    print("TableFormer ACCURATE, as a DataFrame:")
    print(df)
    print()
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    print()

    # Programmatic access: the growth column for North/Hardware, exactly
    # the kind of downstream use a Markdown table would make you re-parse.
    north_hardware = df[(df["Region"] == "North") & (df["Product Line"] == "Hardware")]
    print("North / Hardware row:")
    print(north_hardware.to_string(index=False))


if __name__ == "__main__":
    main()
