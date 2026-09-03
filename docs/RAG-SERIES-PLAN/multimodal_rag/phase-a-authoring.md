# Phase A: Author the `multimodal_rag` course

**Status: authored, partially verified. All 26 lessons written and pass
py_compile. Lessons 1-17 (all of Beginner, Intermediate 10-17) verified
live against the real Gemini API, including a confirmed-genuine Lesson 7
cross-modal retrieval (image beat every text chunk on real embedding
scores) and a real bug fixed in Lesson 13 (query rephrased so k-balancing
actually has something to prove against live embeddings). Lessons 18-26
(Intermediate 18, all of Advanced) remain unverified - blocked on the
`EmbedContentRequestsPerDayPerUserPerProjectPerModel-FreeTier` daily
quota (1000/day), which did not reliably reset within the same session
despite one successful probe call, so treat any single successful check
with caution and re-verify quota headroom before resuming. Resume at
Lesson 18 (`02_intermediate/18_intermediate_checkpoint_project/lesson.py`)
once quota is confirmed available; pay particular attention to Lesson 20
(chromadb introduction - this is where the `image_path=""` vs `None`
metadata convention starts to matter) and Lesson 25 (capstone - confirm
cross-modal retrieval still works once on chromadb).**
Mirrors [`../naive_rag/phase-a-authoring.md`](../naive_rag/phase-a-authoring.md)'s
structure and conventions exactly - only the content differs.

## To-Do List

- [x] Get user approval on this syllabus before writing any files
- [x] Lesson 22's `ingest()`/`ask()` implements the series' shared
      `Strategy` protocol (`docs/RAG-SERIES-PLAN/README.md`): `ingest(docs)
      -> State` where `State` here is a mixed-modality `chroma_collection`,
      `ask(query, state, k) -> str`. Say explicitly in that lesson's
      README what lives inside `State`, so `adaptive_rag` L21 can wire
      this in without reading the full implementation.
- [x] Lesson 16 (minimal evaluation) references `naive_rag` L17's "Why
      this doesn't generalize (yet)" section (sample-size limits,
      tune/eval contamination) instead of re-deriving it.
- [x] Lesson 1 names captioning-then-embed as *one* implementation choice
      for multimodal retrieval, not the only one - one sentence
      contrasting it with joint embedding spaces (CLIP-style models that
      embed images and text into the same vector space directly, no
      captioning step) and stating why this course picks captioning
      (reuses the same Gemini API and embedding pipeline every other
      course already uses, no new account/model family, and the caption
      text is directly inspectable/debuggable) - so a student doesn't
      leave thinking captioning *is* multimodal RAG.
- [x] Lesson 23 (FastAPI wrapper) stays a short recipe reusing
      `naive_rag` L24's pattern almost verbatim rather than re-teaching
      FastAPI from scratch - keep it brief and let Lesson 7-8 (cross-modal
      retrieval, generation with the original image) carry the depth this
      course is actually about.
- [x] Design `lessons/multimodal_rag/fixtures/` - this course is the
      first in the series that needs actual **image files**, not just
      markdown notes. Needs a small set of images (2-4) whose content is
      only discoverable visually (e.g. a diagram or photo with a detail
      not described in any text note), plus a folder of notes similar in
      spirit to `naive_rag`'s, so there's a genuine "text retrieval finds
      nothing, image retrieval does" case for Lesson 7.
- [x] Confirm Gemini's current image-input support in the installed
      `google-genai` SDK version (passing image bytes/`Part` objects to
      `generate_content`) before drafting Lesson 3.
- [x] Scaffold `lessons/multimodal_rag/` structure (tier folders, lesson
      folders, course-level `README.md`)
- [x] Write Beginner tier (9 lessons): sending images to Gemini,
      captioning, embedding captions, mixed text+image retrieval
- [x] Write Intermediate tier (9 lessons): multi-image documents,
      modality metadata, persistence, cross-modal k-balance, failure
      modes, minimal eval, checkpoint
- [x] Write Advanced tier (8 lessons): scale limits of per-query
      captioning, chromadb for the mixed store, modality filtering,
      refactor, service wrapper, capstone, series bridge/retrospective
      lesson
- [x] Add `Pillow` to `pyproject.toml` (basic image loading/resizing);
      confirm no other new dependency is needed beyond `google-genai`
      (already present) and `chromadb` (already present); run `uv sync`
      (Pillow was already present at `pillow>=12.3.0`; `uv sync`
      confirmed green)
- [x] Add the `multimodal_rag` course bullet to the repo root `README.md`
- [ ] Spot-check every lesson's `lesson.py` actually runs against a real
      `GOOGLE_API_KEY` and matches its README's "Expected output"
      (deferred: today's `GOOGLE_API_KEY` is quota-exhausted, see status
      line above)

## Course 6 Spec: Multimodal RAG

- **Repo folder**: `lessons/multimodal_rag/`
- **Portfolio slug**: `multimodal-rag`
- **Title**: "Multimodal RAG: Retrieving Across Text and Images"
- **Topic** (portfolio): `Retrieval` (existing value, no catalog edit
  needed)
- **Model**: Gemini (`GOOGLE_API_KEY`), using its native image-input
  support for captioning and re-examining retrieved images at generation
  time, plus the same text embedding endpoint used throughout the series
  for both text chunks and image captions.
- **New dependency**: `Pillow` (lightweight, no server) for basic image
  loading/resizing before sending images to Gemini.
- **Relationship to prior courses**: reuses `naive_rag`'s exact pipeline
  shape (embed → store → retrieve → generate) unchanged for the text
  half; the only new idea is captioning images into embeddable text and
  re-attaching the original image at generation time. Lesson 2 recaps
  text-only retrieval's blind spot before introducing images.

### Lesson breakdown (26 lessons across 3 tiers, draft)

**Beginner - captioning images into a retrievable form (9 lessons)**
1. What Multimodal RAG is: documents aren't just text, and images carry retrievable information too - including one sentence naming captioning-then-embed (this course's approach) as one implementation choice among others, distinct from joint embedding spaces (CLIP-style models with no captioning step), and why this course picks captioning (reuses the same Gemini API/embedding pipeline every other course already uses, and the caption text is directly inspectable)
2. Recap: text-only retrieval's blind spot - a question only answerable by looking at an image
3. Sending an image to Gemini: your first multimodal `generate_content` call
4. Captioning an image: prompting Gemini to describe it in retrievable detail
5. Embedding image captions with the same embedding pipeline used for text chunks
6. A mixed vector store: text chunks and image captions in one list, retrieved together
7. Retrieval across modalities: a query that matches an image caption, not any text chunk
8. Generation with the original image: re-attaching the actual image (not just its caption) when it's retrieved, so Gemini can look at it directly
9. Beginner checkpoint: a CLI Q&A over a small folder of notes and images

**Intermediate - multiple images, metadata, and evaluation (9 lessons)**
10. Captioning multiple images per document (e.g. several figures in one source)
11. Metadata for multimodal chunks: modality (text/image), source file, figure number
12. Persisting captions and embeddings so images aren't re-captioned every run
13. Balancing k across modalities so image results aren't drowned out by (or don't drown out) text results
14. Prompting for grounded answers that cite whether a fact came from text or an image
15. Failure modes: a caption losing detail the image actually had, or a query matching a caption without the image containing what's asked
16. Minimal evaluation: precision@k on a labeled set mixing text-answerable and image-answerable questions
17. Handling images embedded in a PDF page (extracting them before captioning)
18. Intermediate checkpoint: a notes-and-diagrams search assistant with citations noting modality

**Advanced - graduating the mixed store, and a capstone (8 lessons)**
19. Where per-query image re-captioning gets expensive: cost and latency of vision calls at scale
20. Introducing `chromadb` for the mixed text+image-caption store, same pattern as `naive_rag`'s Advanced tier
21. Metadata filtering by modality with `chromadb` (text-only, image-only, or both)
22. Refactoring into `ingest()`/`ask()` functions handling both modalities
23. Wrapping it as a small callable service (FastAPI) that accepts text queries and returns cited text/image answers
24. Serving the original image back to the caller (not just describing it) when an image is the best match
25. Advanced capstone: a complete multimodal RAG service over a folder of notes and images
26. Where Multimodal RAG hits a wall - a short bridge lesson naming the failure modes that motivate Adaptive RAG (sets up course 7, no code)

Numbers/exact count may shift once READMEs are drafted, same caveat as
prior courses' syllabi.

## File Tree (`lessons/multimodal_rag/`, draft)

```
lessons/multimodal_rag/
├── README.md
├── 01_beginner/
│   ├── 01_what_is_multimodal_rag/
│   ├── 02_the_blind_spot_of_text_only_retrieval/
│   ├── 03_sending_an_image_to_gemini/
│   ├── 04_captioning_an_image/
│   ├── 05_embedding_image_captions/
│   ├── 06_a_mixed_vector_store/
│   ├── 07_retrieval_across_modalities/
│   ├── 08_generation_with_the_original_image/
│   └── 09_beginner_checkpoint_project/
├── 02_intermediate/
│   ├── 10_captioning_multiple_images_per_document/
│   ├── 11_modality_metadata/
│   ├── 12_persisting_captions_and_embeddings/
│   ├── 13_balancing_k_across_modalities/
│   ├── 14_prompting_for_modality_cited_answers/
│   ├── 15_failure_modes_of_captioning_and_matching/
│   ├── 16_minimal_evaluation_text_vs_image_questions/
│   ├── 17_extracting_images_from_a_pdf/
│   └── 18_intermediate_checkpoint_project/
├── 03_advanced/
│   ├── 19_where_per_query_captioning_gets_expensive/
│   ├── 20_introducing_chromadb_for_the_mixed_store/
│   ├── 21_metadata_filtering_by_modality/
│   ├── 22_refactoring_into_ingest_and_ask/
│   ├── 23_wrapping_it_as_a_service/
│   ├── 24_serving_the_original_image_back/
│   ├── 25_advanced_capstone_project/
│   └── 26_where_multimodal_rag_hits_a_wall/
└── fixtures/                  # notes/ + images/
```

## Execution Steps (draft, mirrors `naive_rag`)

1. Present this syllabus to the user and get approval before writing any
   lesson files.
2. Source or create the small image fixture set (see To-Do List above) -
   this is the one genuinely new kind of asset this course needs.
3. Scaffold `lessons/multimodal_rag/` matching `lessons/naive_rag/`'s
   structure exactly.
4. Write the lessons tier by tier, spot-checking `uv run python
   lessons/multimodal_rag/<tier>/<lesson>/lesson.py` against a real
   `GOOGLE_API_KEY` as each tier completes.
5. Update repo-wide files:
   - `pyproject.toml`: add `Pillow`.
   - Root `README.md`: add the `multimodal_rag` course bullet.
6. Run `uv sync` and do a final full read-through pass of the new course
   folder.

## Verification

Every lesson's `lesson.py` actually runs and produces the output
documented in its README's "Expected output" section; `uv sync` succeeds
after the `Pillow` dependency add. Lesson 7's cross-modal retrieval demo
should retrieve the image (not a text chunk) for a question only the
image answers - if it doesn't, the fixture images/captions or the
question likely need adjusting so the lesson's point actually lands.
