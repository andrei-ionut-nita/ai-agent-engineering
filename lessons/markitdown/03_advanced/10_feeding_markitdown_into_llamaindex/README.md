# Lesson 10: feeding MarkItDown into LlamaIndex

## Two libraries, one clean handoff

MarkItDown's job is narrow: turn a file into a Markdown string. It has
no idea what happens to that string next. LlamaIndex's `Document` is
just as narrow from the other direction: it wraps a string (plus
optional metadata) so an index can chunk, embed, and retrieve it. The
integration between them is nothing more than passing one library's
output into the other's constructor:

```python
result = md.convert(path)
document = Document(text=result.markdown, metadata={"source": path.name})
```

This lesson assumes basic familiarity with
[`lessons/llamaindex/`](../../../llamaindex/) Lessons 1-4 (`Settings`,
`Document`, `VectorStoreIndex`, query engines), it's a soft
prerequisite the same way this course notes `lessons/liteparse/`'s
existence, see that course if any of `Settings.llm`,
`VectorStoreIndex.from_documents`, or `.as_query_engine()` are
unfamiliar.

## What each library is actually responsible for

| Step | Library | What happens |
|---|---|---|
| File to Markdown | MarkItDown | `.convert(path)` → `.markdown` string |
| Markdown to `Document` | Neither, just Python | Wrap the string, attach `metadata={"source": ...}` |
| `Document`s to searchable index | LlamaIndex | `VectorStoreIndex.from_documents(documents)`, embeds and stores each |
| Question to answer | LlamaIndex | `.as_query_engine().query(question)`, retrieve + synthesize |

By the time `VectorStoreIndex.from_documents()` runs, it has no idea
the text came from a `.docx`, a `.pptx`, or a plain `.txt` file,
MarkItDown's involvement already ended.

## Why `office_notice.png` is left out again

Same reasoning as Lesson 5: this lesson's `MarkItDown()` instance has
no LLM client attached, so converting the image fixture here would add
almost no useful text to the index. Lesson 12's capstone brings the
image back in with captioning wired up, so it can actually be found by
a query.

## The code, piece by piece

```python
Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)
```

Exactly the models and configuration confirmed working in
`lessons/llamaindex/`, set once, globally, before any indexing happens.

```python
for filename in SOURCE_FILES:
    result = md.convert(FIXTURES_DIR / filename)
    documents.append(Document(text=result.markdown, metadata={"source": filename}))
```

The handoff itself: convert, wrap, collect. `metadata={"source": filename}`
means every retrieved chunk can be traced back to its original file,
visible in `response.source_nodes` later.

```python
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query(question)
```

From here it's pure LlamaIndex, unrelated to MarkItDown at all.

## Running it

```bash
uv run python lessons/markitdown/03_advanced/10_feeding_markitdown_into_llamaindex/lesson.py
```

This makes real Gemini API calls (embeddings for every document at
index time, one generation call per question), keep that in mind
against a constrained quota.

## Expected output

The retrieval scores and exact answer wording can vary slightly
between runs (embedding similarity and LLM generation are not
perfectly deterministic), this is one real captured run:

```
Converted 5 fixtures into LlamaIndex Documents.

Q: What equipment stipend is available for remote workers, and what does it cover?
A: Remote employees who work from home more than two days per week are eligible for a one-time equipment stipend. This stipend covers the following items up to specific price limits:

- An ergonomic chair (up to $250)
- A second monitor (up to $180)
- A webcam and headset bundle (up to $60)

Any items outside of this approved list require separate manager approval before purchase.

  Source documents used:
    - remote_work_memo.docx (score=0.7445)
    - product_spec.pdf (score=0.5798)

Q: What is the TrailLight lantern's battery life requirement?
A: The TrailLight lantern requires a battery life of at least 20 hours on low brightness.

  Source documents used:
    - product_spec.pdf (score=0.7195)
    - release_notes.txt (score=0.6951)
```

Notice the first question retrieved `product_spec.pdf` as a secondary
match even though the answer came entirely from the memo, that's
normal vector-similarity behavior across a small, topically related
document set, not a MarkItDown concern.

## Checkpoint

- **The integration is just a handoff**: `Document(text=result.markdown, ...)`,
  neither library needs to know about the other beyond that.
- **MarkItDown's job ends at a string**: chunking, embedding, and
  retrieval are entirely LlamaIndex's responsibility.
- **`metadata={"source": ...}`**: carries the original filename through
  indexing so retrieved results stay traceable.
- **Soft prerequisite**: this lesson assumes `lessons/llamaindex/`
  Lessons 1-4 (`Settings`, `Document`, `VectorStoreIndex`, query
  engines) are already familiar.

If anything here still feels unclear, ask before moving to Lesson 11.
