# Lesson 14 (Capstone): Mixed folder to Gemini-answered queries

## The whole course, end to end

This capstone combines the OCR-fallback triage from Lesson 11 with the
LlamaIndex tie-in from Lesson 13, run against the entire `sample_data/`
folder, native-text documents and the one genuine scan together. The
pipeline has exactly two stages, and only the second one touches the
network:

1. **Stage 1 (LiteParse, local, no network)**: parse every PDF fast
   with OCR off; for any document whose fast pass yields near-zero
   text, re-parse it with OCR on. Same strategy as Lesson 11, applied
   to build the final document set instead of just printing a table.
2. **Stage 2 (LlamaIndex + Gemini, network)**: index all the resulting
   text, ask it three questions.

No document-parsing API, hosted or otherwise, appears anywhere in this
pipeline. The only network calls are LlamaIndex's embedding calls and
each query's LLM call, both to Gemini, both operating on plain text
that already exists locally by the time they're made.

## Proof the OCR fallback matters, not just a demo of it

The third question, "What time will water service be interrupted?", is
only answerable because of Stage 1's OCR fallback. That fact lives
exclusively in `scanned_notice.pdf`, a page with zero native PDF text
(Lesson 8). Without the fallback, that document would contribute an
empty `Document` to the index (Lesson 13's simpler pipeline explicitly
skipped it for this reason), and this question would have nothing to
retrieve a correct answer from. Watching the third answer come back
correct is the capstone's actual proof that the fallback pipeline
works end to end, not just that each piece works in isolation.

## The code, piece by piece

```python
def parse_folder_with_ocr_fallback(folder: Path) -> list[Document]:
    parser_no_ocr = liteparse.LiteParse(ocr_enabled=False, quiet=True)
    parser_ocr = liteparse.LiteParse(ocr_enabled=True, quiet=True)
    for pdf_path in sorted(folder.glob("*.pdf")):
        result = parser_no_ocr.parse(pdf_path)
        if len(result.text.strip()) < NEAR_ZERO_TEXT_CHARS:
            result = parser_ocr.parse(pdf_path)
        documents.append(Document(text=result.text, metadata={"source": ..., "ocr_used": ...}))
```

Same fallback logic as Lesson 11, now producing LlamaIndex `Document`
objects directly, with `ocr_used` recorded in metadata alongside
`source`, so it's visible afterward which documents needed the slower
path.

```python
Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)
index = VectorStoreIndex.from_documents(documents)
```

Identical to Lesson 13, just built from all 5 documents this time
instead of 4.

## Running it

```bash
uv run python lessons/liteparse/03_advanced/14_advanced_capstone_project/lesson.py
```

## Expected output

```
Stage 1: LiteParse, local, no network, OCR only where the fast pass yielded near-zero text:
  employee_handbook.pdf: 1070 chars (ocr_used=False)
  intake_form.pdf: 158 chars (ocr_used=False)
  product_spec.pdf: 677 chars (ocr_used=False)
  scanned_notice.pdf: 183 chars (ocr_used=True)
  vendor_memo.pdf: 242 chars (ocr_used=False)

5 document(s) parsed, 2330 total characters, 1 needed OCR

Stage 2: LlamaIndex + Gemini, indexing and querying (the only network calls in this pipeline):

Q: What are the brightness levels of the Aurora Desk Lamp?
A: The Aurora Desk Lamp features 5 brightness levels, ranging from 200 to 1200 lumens.
   (retrieved from: employee_handbook.pdf, product_spec.pdf)

Q: How many paid vacation days do full-time employees accrue per year?
A: Full-time employees accrue 15 days of paid vacation per year.
   (retrieved from: employee_handbook.pdf, vendor_memo.pdf)

Q: What time will water service be interrupted, according to the building notice?
A: Water service will be interrupted from 9 AM to 1 PM.
   (retrieved from: employee_handbook.pdf, scanned_notice.pdf)
```

Gemini's exact wording is not deterministic and may vary slightly
between runs; the facts should stay consistent, and the third answer
in particular should always correctly cite the 9 AM to 1 PM window that
only exists in the OCR-recovered text.

## Checkpoint

- A production-shaped document pipeline: fast local parsing by default,
  OCR only where a cheap check says it's actually needed, then indexed
  and queried, all without a single hosted parsing API call.
- The OCR fallback isn't just a nice-to-have here, it's the only reason
  one of the three questions is answerable at all.
- Every network call in this pipeline is to Gemini, for embeddings and
  answers, operating on text that was already fully extracted, locally,
  before any of it happened.

This closes the course. If anything across all 14 lessons still feels
unclear, that's worth revisiting before building your own
LiteParse-based pipeline.
