# Lesson 3: converting office documents

## Structure translation, not just text extraction

Lesson 2's plain text file didn't really test MarkItDown, there was no
structure to preserve or lose. Office formats are different: a Word
doc has headings and paragraphs, a slide deck has slides and bullets,
a spreadsheet has rows and columns. This lesson converts one of each
and looks at exactly how that structure maps to Markdown.

| Source format | Structure in the source | Structure in the Markdown output |
|---|---|---|
| `.docx` (Word) | Paragraphs, and paragraphs styled as "Heading 1/2/..." | Plain text lines; only paragraphs using an actual heading *style* become `#` headings |
| `.pptx` (PowerPoint) | Slides, each with a title and bullet points | `<!-- Slide number: N -->` marker per slide, slide title as a heading, bullets as a list |
| `.xlsx` (Excel) | Sheets, each a grid of rows/columns | A Markdown pipe table per sheet, header row becomes the table header |

## A gotcha worth knowing: heading styles vs. bold text

`fixtures/remote_work_memo.docx` has section labels like "Summary"
and "What Is Covered" that look like headings when you read the memo.
But they were written as plain bold text, not with Word's built-in
"Heading 1" paragraph style. MarkItDown's docx converter maps Word's
*style*, not its *visual appearance*, to Markdown headings. Bold text
that looks like a heading stays a plain paragraph. If you need
reliable heading structure out of a docx conversion, the source
document needs to actually use Word's heading styles, formatting
alone isn't enough.

## The code, piece by piece

```python
def show(md: MarkItDown, filename: str, note: str) -> None:
    result = md.convert(FIXTURES_DIR / filename)
    print(f"=== {filename} ===")
    ...
```

Same `.convert()` call as Lesson 2, three times, once per format. The
call itself doesn't change shape at all between formats, MarkItDown
handles the format-specific logic internally based on what it detects.

## Running it

```bash
uv run python lessons/markitdown/01_beginner/03_converting_office_documents/lesson.py
```

## Expected output

```
=== remote_work_memo.docx ===
(Word paragraphs -> Markdown text lines (only real heading-styled text becomes '#'))

Internal Memo: Remote Work Equipment Policy

To: All Northwind Gadgets Staff

From: Facilities and IT Department

Date: June 2026

Summary

Starting this quarter, every employee working remotely more than two

days per week is eligible for a one-time equipment stipend. This memo

explains what is covered, how to request it, and who to contact with

questions.

What Is Covered

The stipend covers the following items:

- An ergonomic chair, up to 250 dollars

- A second monitor, up to 180 dollars

- A webcam and headset bundle, up to 60 dollars

Items outside this list require separate manager approval before

purchase.

How to Request Reimbursement

Employees should submit receipts through the internal expense portal

within thirty days of purchase. Reimbursements are processed on the

regular payroll cycle following approval, typically within two weeks.

Questions

Direct any questions about this policy to the Facilities team at the

internal helpdesk, or to your manager during your next one-on-one.

=== onboarding_deck.pptx ===
(Each slide -> a '<!-- Slide number: N -->' marker + heading + bullet list)

<!-- Slide number: 1 -->
# Q3 Onboarding Overview
Northwind Gadgets: Internal Training Deck

<!-- Slide number: 2 -->
# What New Hires Need in Week One
Get their laptop imaged and VPN access approved
Complete the safety and compliance training module
Meet their onboarding buddy for a 30 minute chat
Set up their desk in the north wing, third floor

<!-- Slide number: 3 -->
# Common First-Week Questions
Where is the parking validation kiosk?
Who approves expense reports under $200?
How do I request a second monitor?

=== expense_report.xlsx ===
(Spreadsheet rows/columns -> a Markdown pipe table)

## Expenses
| Date | Category | Description | Amount USD |
| --- | --- | --- | --- |
| 2026-06-02 | Travel | Round-trip flight to Denver conference | 412.50 |
| 2026-06-03 | Meals | Team dinner with Denver sales office | 96.20 |
| 2026-06-05 | Supplies | Replacement laptop charger | 39.99 |
| 2026-06-10 | Software | Annual license renewal, design tool | 228.00 |
| 2026-06-14 | Travel | Taxi from airport to downtown office | 31.75 |
```

Notice the `.xlsx` sheet name ("Expenses") became a `##` heading above
its table, and the pptx's bullet points lost their bullet markers in
this particular deck (they were plain lines within a text box, not a
true PowerPoint bulleted list placeholder), another instance of the
same lesson from the docx case: MarkItDown maps the source format's
actual structure, not how the content merely looks when you view it.

## Checkpoint

- **docx**: paragraphs become text lines; only Word's built-in heading
  *styles*, not bold formatting, become Markdown `#` headings.
- **pptx**: each slide gets an HTML-comment marker, its title becomes
  a heading, true bulleted-list placeholders become Markdown lists.
- **xlsx**: each sheet becomes a Markdown pipe table, sheet name as a
  heading above it.
- **General rule**: MarkItDown follows the source document's actual
  structural metadata, not its visual appearance, worth checking your
  real documents if the converted structure looks off.

If anything here still feels unclear, ask before moving to Lesson 4.
