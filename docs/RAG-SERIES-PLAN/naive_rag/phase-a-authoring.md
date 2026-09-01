# Phase A: Author the `naive_rag` course

**Status: complete.** All 26 lessons authored and verified against the
real Gemini API.

Repo: `/home/nolan/Documents/Projects/ai-agent-engineering` (no template/
CONTRIBUTING exists there - the pattern to mirror is the existing courses
themselves, confirmed structure below).

## To-Do List

- [x] Save the plan to `ai-agent-engineering/docs/RAG-SERIES-PLAN/` as the
      standing reference for this course and the 6 planned after it
- [x] Draft the 26-lesson syllabus table for `naive_rag` and get user
      approval before writing any files (Beginner/Intermediate/Advanced,
      slug/title/concept/checkpoint per lesson)
- [x] Scaffold `lessons/naive_rag/` structure (tier folders, lesson
      folders, course-level `README.md`)
- [x] Write Beginner tier (9 lessons): hand-rolled embeddings, similarity,
      chunking, retrieval, generation, end-to-end script, checkpoint
- [x] Write Intermediate tier (9 lessons): chunking quality, metadata,
      persistence, thresholding, grounded prompting, failure modes,
      minimal eval, checkpoint
- [x] Write Advanced tier (8 lessons): scale limits, `chromadb`
      migration, metadata filtering, refactor to functions, service
      wrapper, capstone, series bridge lesson
- [x] Add `chromadb` to `pyproject.toml`; run `uv sync`
- [x] Add the `naive_rag` course bullet to the repo root `README.md`
- [x] Spot-check every lesson's `lesson.py` actually runs against a real
      `GOOGLE_API_KEY` and matches its README's "Expected output"

## Course 1 Spec: Naive RAG

- **Repo folder**: `lessons/naive_rag/` (new, top-level, sibling to the
  other 16 course folders)
- **Portfolio slug**: `naive-rag`
- **Title**: "Naive RAG: Building the Baseline from Scratch"
- **Topic** (portfolio): `Retrieval` (existing value, no catalog edit
  needed)
- **Model**: Gemini, matching every other course (`GOOGLE_API_KEY`), using
  `google-genai`'s embedding endpoint (`text-embedding-004` or current
  equivalent) for embeddings and a Gemini chat model for generation - no
  new API key or account needed beyond what the repo already requires.
- **New dependency**: `chromadb` (added to `pyproject.toml`, used only in
  the Advanced tier). No Docker/Postgres/Redis requirement - deliberately
  the lightest-setup course in the repo, matching "start with the absolute
  simplest one."

### Lesson breakdown (26 lessons across 3 tiers)

**Beginner - hand-rolled RAG, one piece at a time (9 lessons)**
1. What Naive RAG is and why build it by hand first
2. Your first embedding call (Gemini embeddings API, a vector as a list of floats)
3. Cosine similarity by hand (what "similar meaning" means as a number)
4. Chunking a document into passages
5. An in-memory vector store (list of `{text, embedding}` dicts)
6. Retrieval: embed the query, rank chunks by similarity, take top-k
7. Generation: stuffing retrieved chunks into a prompt
8. End-to-end: one script that answers a question about one document
9. Beginner checkpoint: CLI Q&A over a small folder of text files

**Intermediate - where naive RAG breaks, and the fixes that stay "naive" (9 lessons)**
10. Chunk size and overlap: same document, bad vs. good chunking side by side
11. Structure-aware chunking (splitting on headings/paragraphs instead of fixed size)
12. Multiple documents and metadata (source filename, chunk index, page)
13. Persisting the vector store to disk (JSON) instead of re-embedding every run
14. Choosing k and similarity thresholds (dropping irrelevant top-k hits)
15. Prompting for grounded answers (citing sources, saying "I don't know")
16. Failure modes by hand: a multi-hop question and a split-across-chunks answer, both fail visibly
17. Minimal evaluation: a small labeled Q&A set, manual precision@k
18. Intermediate checkpoint: a notes-search assistant over the user's own markdown folder, with citations

**Advanced - graduating the hand-rolled store, and a capstone (8 lessons)**
19. Where linear-scan cosine similarity breaks down at scale
20. Introducing `chromadb` (in-memory) as a drop-in replacement for the list-based store
21. Re-pointing ingestion/retrieval at chromadb, same interface as Lesson 6-7
22. Metadata filtering with chromadb
23. Refactoring the pipeline into reusable functions (`ingest()`, `ask()`)
24. Wrapping it as a small callable service (CLI or minimal FastAPI endpoint)
25. Advanced capstone: a complete naive RAG app over a real folder of documents, with its known limitations documented in the README
26. Where naive RAG hits a wall - a short bridge lesson naming the specific failure modes that motivate Hybrid/Graph/Corrective/Agentic RAG (sets up course 2, no code)

Numbers/exact count may shift slightly once READMEs are drafted (e.g. if
two adjacent concepts merge into one lesson) - the tier shape and rough
count is the target, not a hard requirement.

## File Tree (`lessons/naive_rag/`)

```
lessons/naive_rag/
├── README.md                                    # course index (tier tables)
├── 01_beginner/
│   ├── 01_what_is_naive_rag/
│   │   ├── README.md
│   │   └── lesson.py
│   ├── 02_your_first_embedding/
│   │   ├── README.md
│   │   └── lesson.py
│   ├── 03_cosine_similarity_by_hand/
│   ├── 04_chunking_a_document/
│   ├── 05_an_in_memory_vector_store/
│   ├── 06_retrieval_top_k/
│   ├── 07_generation_stuffing_the_prompt/
│   ├── 08_end_to_end_single_document_qa/
│   └── 09_beginner_checkpoint_project/          # CLI Q&A over a folder
├── 02_intermediate/
│   ├── 10_chunk_size_and_overlap/
│   ├── 11_structure_aware_chunking/
│   ├── 12_multiple_documents_and_metadata/
│   ├── 13_persisting_the_vector_store/
│   ├── 14_choosing_k_and_thresholds/
│   ├── 15_prompting_for_grounded_answers/
│   ├── 16_failure_modes_by_hand/
│   ├── 17_minimal_evaluation_precision_at_k/
│   └── 18_intermediate_checkpoint_project/      # notes-search assistant
├── 03_advanced/
│   ├── 19_where_linear_scan_breaks_down/
│   ├── 20_introducing_chromadb/
│   ├── 21_repointing_retrieval_at_chromadb/
│   ├── 22_metadata_filtering_with_chromadb/
│   ├── 23_refactoring_into_ingest_and_ask/
│   ├── 24_wrapping_it_as_a_service/
│   ├── 25_advanced_capstone_project/            # full naive RAG app
│   └── 26_where_naive_rag_hits_a_wall/          # bridge to course 2, no code
└── fixtures/                                    # sample .txt/.md docs for lessons to embed
```

Every leaf lesson folder (all 26) has exactly `README.md` + `lesson.py`,
same as every other course in the repo - only the tier/checkpoint folders
shown in full above to keep the tree readable; the remaining lesson
folders under `02_intermediate/` and `03_advanced/` follow the identical
two-file shape.

## Execution Steps

1. Create `lessons/naive_rag/` following the exact structure every other
   course uses (verified against `lessons/pgvector/` and `lessons/langchain/`):
   - `lessons/naive_rag/01_beginner/`, `02_intermediate/`, `03_advanced/`
   - Each lesson: `NN_snake_case_slug/README.md` + `lesson.py`
   - Checkpoint lessons: `README.md` only pattern differs (`## Try this
     yourself` instead of `## Checkpoint`), no separate `lesson.py` is
     required unless the checkpoint has its own runnable script (existing
     courses do give checkpoints their own `lesson.py` - follow that).
   - Lesson `README.md` shape to match: `# Lesson N: Title` → concept intro →
     `## The code, piece by piece` → `## Running it` → `## Expected output`
     → `## Checkpoint` (bullet recap + "ask before moving on" nudge).
   - `lesson.py` shape to match: module docstring with the run command,
     `load_dotenv()`, a `def main() -> None:`, `if __name__ == "__main__":`.
   - Course-level `lessons/naive_rag/README.md`: index table per tier,
     matching `lessons/langchain/README.md`'s format.
2. Present the 26-lesson syllabus table (number, slug, tier, title,
   concept, checkpoint) to the user for approval before writing any lesson
   files - same gate discipline as `/write-course` Phase 2, applied here
   since this is new authoring, not a port.
3. Write the lessons tier by tier, spot-checking `uv run python
   lessons/naive_rag/<tier>/<lesson>/lesson.py` actually runs against a
   real `GOOGLE_API_KEY` as each tier completes (not just at the end).
4. Update repo-wide files:
   - `pyproject.toml`: add `chromadb` to shared dependencies.
   - Root `README.md`: add the `naive_rag` bullet to the course list
     (17th course), plus a short Setup note only if chromadb needs
     anything beyond `uv sync` (it shouldn't, in-memory mode).
   - No `docker-compose.yml` / `.env.example` changes needed (no external
     service).
5. Run `uv sync` and do a final full read-through pass of the new course
   folder.

## Verification

Every lesson's `lesson.py` actually runs (`uv run python
lessons/naive_rag/<tier>/<lesson>/lesson.py`) and produces the output
documented in its README's "Expected output" section; `uv sync` succeeds
after the `chromadb` dependency add.

Confirmed: all 26 lesson folders have both `README.md` and `lesson.py`,
all pass `py_compile`, `uv sync` succeeds, and lessons were spot-checked
against the live Gemini API tier by tier.
