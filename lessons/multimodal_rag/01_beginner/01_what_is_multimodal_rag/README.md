# Lesson 1: What Is Multimodal RAG?

## Where we left off

`naive_rag`, `hybrid_rag`, `graph_rag`, and `corrective_rag` all share one
assumption you probably stopped noticing: every document is text. Chunk
it, embed it, retrieve it, generate from it, all four stages only ever
touch strings. That assumption is false for a lot of real documents. A
lab notebook has photos of an instrument's dial. A repair log has a
close-up of a part with a spec stamped on it. A slide deck has a chart
whose axis labels carry the actual number a question is asking about.
None of that is retrievable by a pipeline that only ever reads text,
no matter how good the chunking or the embedding model is, because the
information was never turned into text in the first place.

**Multimodal RAG** is retrieval-augmented generation extended to cover
that case: documents (and the facts inside them) can be images as well
as text, and both need to end up retrievable by the same query.

## Two different ways to make an image retrievable

There is more than one way to solve this, and this course commits to
one of them on purpose, not because it's the only correct answer:

- **Captioning-then-embed** (what this course builds): describe the
  image in words with a vision-capable model, then embed that
  description with the exact same text-embedding pipeline every prior
  course in this series already uses. Retrieval never touches pixels
  directly, it retrieves *text about* the image.
- **Joint embedding spaces** (CLIP-style models): a model trained to
  embed images and text into the *same* vector space directly, no
  captioning step, so an image's embedding and a matching sentence's
  embedding land close together on their own.

Both are legitimate, shipped approaches to multimodal retrieval, and a
production system sometimes uses both together. This course picks
captioning because it reuses the same Gemini API and text-embedding
pipeline every other course in this series already uses (no new
account, no new model family to learn), and because a caption is
plain text you can read, log, and debug directly, where a CLIP-style
joint embedding is an opaque vector you can't inspect at all. The cost
of that choice is real too, and Lesson 19 comes back to it: a caption
is a lossy summary of an image, written once by a model that might miss
a detail a joint embedding would have captured directly from the
pixels. **If you finish this course thinking captioning is the only way
to do multimodal RAG, or that it has no downsides, re-read this
section.**

## The code, piece by piece

```python
image_path = IMAGES_DIR / "derailleur-hanger-diagram.png"
response = client.models.generate_content(model=CHAT_MODEL, contents=QUESTION)
```

Same call as `naive_rag` Lesson 1: a bare text question, no context, no
image attached, nothing retrieved. `QUESTION` asks for a fact that only
exists inside `derailleur-hanger-diagram.png` (see
`fixtures/README.md`), a torque spec printed on a part in a diagram
Gemini has never seen and this call never shows it. The point isn't
"the model doesn't know a torque spec", it's narrower than that: even
if this course later builds full text-only Naive RAG over
`fixtures/notes/`, that fact still won't surface, because it was never
written down as text anywhere. Lesson 2 proves that narrower claim
directly.

## Running it

```bash
uv run python lessons/multimodal_rag/01_beginner/01_what_is_multimodal_rag/lesson.py
```

## Expected output

```
Question: What's the torque spec for the rear derailleur hanger bolt, and what color is it printed in?

Gemini, with no context and no image:
<a guess, or an "I don't know" - varies each run>

Multimodal RAG extends Naive RAG's four stages with one new idea:
  1. Caption  - describe an image in retrievable text (this course's approach)
  2. Embed    - the caption, with the same pipeline used for text chunks
  3. Retrieve - text chunks and image captions together, ranked by one query
  4. Generate - re-attach the *original image* (not just its caption) when it's the best match
```

## Checkpoint

- **Multimodal RAG**: retrieval-augmented generation where documents
  can be images as well as text, and both are retrievable by the same
  query.
- **Captioning-then-embed** (this course): describe an image in text,
  embed the description with the existing text pipeline. Retrieval
  never touches pixels.
- **Joint embedding spaces** (CLIP-style, not this course): embed
  images and text into one shared vector space directly, no captioning
  step. A real system may use either, or both.
- Why this course picks captioning: it reuses the exact pipeline every
  prior course already built, and a caption is inspectable text, not
  an opaque vector.
- A fact that only exists inside an image is invisible to a pipeline
  that only ever reads text, no matter how good that pipeline is.

If anything here still feels unclear, ask before moving to Lesson 2.
