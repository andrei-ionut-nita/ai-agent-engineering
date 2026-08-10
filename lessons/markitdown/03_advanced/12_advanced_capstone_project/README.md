# Lesson 12 (Advanced capstone): one index, every format

## Everything this course covered, in one script

This capstone doesn't introduce new MarkItDown or LlamaIndex API. It
combines three pieces already built in this course:

- **Lesson 6**: an OpenAI-shaped client pointed at Gemini's
  OpenAI-compatible endpoint, attached to `MarkItDown` via
  `llm_client`/`llm_model`, so images get real descriptions instead of
  near-empty output.
- **Lesson 10**: the MarkItDown-to-LlamaIndex handoff, `Document(text=result.markdown, metadata=...)`,
  feeding a `VectorStoreIndex`.
- **Lessons 5 and 9**: the "convert everything in this folder" loop.

The difference from Lesson 10 is what's in the loop: this time it's
the *entire* `fixtures/` folder, all six files, including
`office_notice.png`. With captioning wired in, the image genuinely
contributes retrievable content, not something to skip like in
Lessons 5 and 10.

## Proving the index actually spans every format

Three questions, each answerable from a different source format,
confirm the index isn't secretly only working off the text-native
files:

| Question | Answer lives in |
|---|---|
| "When is the office closed and why?" | `office_notice.png`, via LLM captioning |
| "What laptop charger expense was submitted and on what date?" | `expense_report.xlsx` |
| "What onboarding buddy meeting happens in week one?" | `onboarding_deck.pptx` |

If the top-scoring source document for each answer matches the format
in that table, the whole pipeline, six formats in, one Gemini-backed
index, worked end to end.

## The code, piece by piece

```python
caption_client = OpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
md = MarkItDown(llm_client=caption_client, llm_model="gemini-3.5-flash-lite")
```

Lesson 6's client, reused here as the single `MarkItDown` instance
this whole capstone runs on, every conversion, not just the image
one, goes through this same instance.

```python
for source_path in sorted(p for p in FIXTURES_DIR.iterdir() if p.is_file()):
    result = md.convert(source_path)
    documents.append(Document(text=result.markdown, metadata={"source": source_path.name}))
```

No skip list this time, Lesson 10's `SOURCE_FILES` list and Lesson 5's
`SKIP` set both excluded the PNG, here it's included because the
captioning client makes it worth including.

## Running it

```bash
uv run python lessons/markitdown/03_advanced/12_advanced_capstone_project/lesson.py
```

This is the most Gemini-call-heavy lesson in the course: one
captioning call, six embedding calls (one per document at index time),
three generation calls (one per question). Run it once, deliberately,
not in a loop.

## Expected output

The captioned image text and generated answers can vary slightly
between runs, this is one real captured run, and the retrieval scores
confirm each answer's top source matched the table above:

```
Converted expense_report.xlsx (435 chars)
Converted office_notice.png (270 chars)
Converted onboarding_deck.pptx (519 chars)
Converted product_spec.pdf (819 chars)
Converted release_notes.txt (293 chars)
Converted remote_work_memo.docx (1014 chars)

Indexing 6 documents across 6 different source formats...

Q: When is the office closed and why?
A: The Northwind Gadgets main office will be closed on Monday, July 6th for the observed holiday.
  Source documents used:
    - office_notice.png (score=0.7012)
    - remote_work_memo.docx (score=0.6021)

Q: What laptop charger expense was submitted and on what date?
A: A replacement laptop charger expense of 39.99 USD was submitted on 2026-06-05.
  Source documents used:
    - expense_report.xlsx (score=0.6823)
    - remote_work_memo.docx (score=0.6570)

Q: What onboarding buddy meeting happens in week one?
A: New hires meet with their onboarding buddy for a 30-minute chat during their first week.
  Source documents used:
    - onboarding_deck.pptx (score=0.6675)
    - remote_work_memo.docx (score=0.5881)
```

Every top-scoring source matches the format expected to hold the
answer, confirming the captioned image is genuinely retrievable
alongside the office documents, not just present in the index but
unreachable.

## Checkpoint

- **This capstone is a combination, not new API**: Lesson 6's
  captioning client + Lesson 10's handoff + Lesson 5/9's folder loop,
  applied to the full fixture set.
- **A captioned image is a real, retrievable index entry**: with an
  LLM client attached, `office_notice.png` answered a question just
  like any text-native format did.
- **One index, six formats, one query interface**: the whole point of
  MarkItDown's breadth, upstream of LlamaIndex, format differences
  disappear once everything becomes Markdown text.

That's the course. If anything across these twelve lessons still
feels unclear, this is the point to go back and ask about it.
