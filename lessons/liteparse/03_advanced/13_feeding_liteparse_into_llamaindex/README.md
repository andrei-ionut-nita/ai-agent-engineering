# Lesson 13: Feeding LiteParse into LlamaIndex

## Soft prerequisite

This lesson assumes basic familiarity with the
[llamaindex](../../../llamaindex/) course, specifically `Document`
(Lesson 2) and `VectorStoreIndex` (Lesson 4). If those are new, a quick
read through that course's first four lessons will make this one click
faster; this lesson doesn't re-explain what a vector index is.

## Where the network call actually happens

This pipeline has two distinct halves that are easy to blur together:

1. **Parsing** (LiteParse): entirely local, no network call, covered in
   every earlier lesson in this course.
2. **Indexing and querying** (LlamaIndex + Gemini): this is where the
   network enters, once, for embedding the text and once per query for
   the LLM's answer.

The PDF never leaves your machine. Only the *extracted text* (already
plain strings by the time LlamaIndex sees them) goes to Gemini, for
embeddings and for answering questions, the exact opposite of a hosted
parsing API where the raw document itself gets uploaded.

## The code, piece by piece

```python
parser = liteparse.LiteParse(ocr_enabled=False, quiet=True)
for pdf_path in pdf_paths:
    result = parser.parse(pdf_path)
    documents.append(Document(text=result.text, metadata={"source": pdf_path.name}))
```

Each PDF becomes one `Document`. `metadata={"source": ...}` carries the
originating filename through the index, so later a query result can be
traced back to which file it came from, the whole-document equivalent
of the per-page numbers Lesson 4 introduced.

`scanned_notice.pdf` is deliberately excluded from this lesson's batch:
with `ocr_enabled=False` its `.text` comes back empty (Lesson 8), and
an empty `Document` contributes nothing but noise to the index. Lesson
14's capstone handles the OCR-fallback case properly, this lesson keeps
the pipeline simple and focuses on the LlamaIndex tie-in itself.

```python
Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
```

Standard LlamaIndex setup (llamaindex course, Lessons 1-4): configure
the global `Settings`, build a `VectorStoreIndex` from the `Document`
list, get a query engine.

```python
response = query_engine.query(question)
sources = {node.metadata.get("source") for node in response.source_nodes}
```

Each query retrieves relevant chunks across ALL indexed documents (not
just one), and `response.source_nodes` reports which document(s) the
answer was actually retrieved from, using the `metadata["source"]`
LiteParse's output was tagged with earlier. This lesson's two questions
each target a different source document, confirming the index is doing
real cross-document retrieval, not just echoing whichever document
happened to be indexed first.

## Running it

```bash
uv run python lessons/liteparse/03_advanced/13_feeding_liteparse_into_llamaindex/lesson.py
```

## Expected output

```
Parsed 4 PDF(s) locally with LiteParse, no network call:
  employee_handbook.pdf: 1070 characters
  intake_form.pdf: 158 characters
  product_spec.pdf: 677 characters
  vendor_memo.pdf: 242 characters

Q: What are the brightness levels of the Aurora Desk Lamp?
A: The Aurora Desk Lamp has 5 brightness levels, ranging from 200 to 1200 lumens.
   (retrieved from: employee_handbook.pdf, product_spec.pdf)

Q: How many paid vacation days do full-time employees accrue per year?
A: Full-time employees accrue 15 days of paid vacation per year.
   (retrieved from: employee_handbook.pdf, vendor_memo.pdf)
```

The exact wording of Gemini's answers is not deterministic and may
vary slightly between runs; the facts should stay consistent since
they're grounded in the parsed text. `source_nodes` retrieval will
usually include the file the fact actually came from, but with an
index this small (4 short documents), an unrelated file can sometimes
be retrieved too, the answer's correctness matters more than the
retrieved-set being perfectly tight.

## Checkpoint

- The PDF itself never leaves your machine, only LiteParse's extracted
  text goes to LlamaIndex/Gemini, and only for embeddings and answers.
- `metadata={"source": ...}` on each `Document` carries provenance
  through the index, retrievable via `response.source_nodes`.
- This is the same `VectorStoreIndex`/query engine pattern as the
  llamaindex course, LiteParse is just the local, zero-cost step that
  produces the `Document.text` those Documents are built from.

If anything here still feels unclear, ask before moving to Lesson 14,
the capstone.
