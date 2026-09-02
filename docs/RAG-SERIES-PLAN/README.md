# Naive RAG Course: From ai-agent-engineering to the Portfolio

Each course in the series gets its own subfolder here, with one file per
phase (Phase A: author in this repo, Phase B: publish to the portfolio):

- [`naive_rag/`](./naive_rag/) - Course 1, Naive (Standard) RAG.
  [Phase A](./naive_rag/phase-a-authoring.md) **complete**;
  [Phase B](./naive_rag/phase-b-publishing.md) **not started**, awaiting
  user go-ahead.
- [`hybrid_rag/`](./hybrid_rag/) - Course 2, Hybrid (dense + sparse) RAG.
  [Phase A](./hybrid_rag/phase-a-authoring.md) **complete**;
  [Phase B](./hybrid_rag/phase-b-publishing.md) **not started**, awaiting
  user go-ahead.
- [`graph_rag/`](./graph_rag/) - Course 3, Graph RAG.
  [Phase A](./graph_rag/phase-a-authoring.md) **planned, not started**.
- [`corrective_rag/`](./corrective_rag/) - Course 4, Corrective RAG.
  [Phase A](./corrective_rag/phase-a-authoring.md) **complete**;
  [Phase B](./corrective_rag/phase-b-publishing.md) **not started**,
  awaiting user go-ahead.
- [`agentic_rag/`](./agentic_rag/) - Course 5, Agentic RAG.
  [Phase A](./agentic_rag/phase-a-authoring.md) **planned, not started**.
- [`multimodal_rag/`](./multimodal_rag/) - Course 6, Multimodal RAG.
  [Phase A](./multimodal_rag/phase-a-authoring.md) **planned, not
  started**.
- [`adaptive_rag/`](./adaptive_rag/) - Course 7, Adaptive RAG (series
  closer - depends on courses 2-5 being authored first).
  [Phase A](./adaptive_rag/phase-a-authoring.md) **planned, not
  started**.

Every course's Phase A syllabus needs the user's explicit approval before
any lesson files get written - draft status here means "syllabus exists,"
not "cleared to start."

## Executive Summary

The portfolio's `rag-fundamentals` course already maps all nine RAG
architectures conceptually, but every existing hands-on course in
`ai-agent-engineering` is organized around a **library** (pgvector,
llamaindex, docling...), not an **architecture**. This plan starts a new,
parallel series organized by RAG architecture instead, beginning with the
simplest one: Naive (Standard) RAG.

The new course, `naive_rag`, is built from scratch (raw Gemini calls, a
hand-rolled in-memory vector store, manual cosine similarity) so every
mechanic is visible before any framework hides it, then graduates to
`chromadb` in the Advanced tier as a deliberate "here's what you'd reach
for once you understand this" step. It's full-size (26 lessons, 3 tiers),
matching the depth of the repo's other courses. Once authored and
verified, it's published to `andreinita.co/learning/naive-rag/` using the
existing, already-gated `/write-course` pipeline - this plan does not
reinvent that pipeline, only the new content it will publish.

Six more courses (Hybrid, Graph, Corrective, Agentic, Multimodal, Adaptive
RAG) are named now for naming consistency, but only Naive RAG is built in
this pass.

## Context

The blog post [rag-fundamentals](https://andreinita.co/learning/rag-fundamentals/)
maps nine RAG architectures by complexity, and its 1:1 companion is already
published as a no-code, concept-only course
(`portfolio/src/data/learning/rag-fundamentals.ts`). That course explicitly
says: *"Lessons on specific techniques... go deep hands-on in this site's
pgvector, docling, and llamaindex courses; this course is what to read before
those."*

Those hands-on courses exist, but all of them are **tool-shaped**
(pgvector, llamaindex, docling, markitdown, liteparse, ollama's local RAG
lesson) - none of them is **architecture-shaped**. There is currently no
course that teaches "how do you actually build Naive RAG, mechanically, one
concept at a time" the way `rag-fundamentals` Lesson 4 describes it in
prose. That's the gap this plan fills: a new hands-on course series in
`ai-agent-engineering`, organized by RAG architecture (mirroring the blog's
complexity ordering) instead of by library, starting with the simplest one -
Naive (Standard) RAG - then published to the portfolio's Learning section
via the existing `/write-course` pipeline.

## Decisions (confirmed with user)

- **Tech approach**: build from scratch first - raw Gemini calls, a plain
  Python list as the "vector store," manual cosine similarity - so the
  mechanics are fully visible, not hidden behind a framework (this repo's
  langchain/llamaindex/pgvector courses already cover the framework path).
  Toward the end of the course, graduate to a lightweight real vector
  library (`chromadb`, in-memory mode) as a deliberate "here's what you'd
  reach for once you understand what it's doing" step.
- **Course size**: full-size, matching the depth of pgvector (28 lessons)
  / llamaindex (24 lessons), not a short/thin course - despite Naive RAG
  being architecturally the simplest, there's a full 3-tier course's worth
  of ground (embeddings, chunking, retrieval, generation, tuning,
  evaluation, persistence, graduating to a real vector store, a capstone
  app).
- **Series roadmap**: sketched now (naming only), built one course at a
  time starting with this one.

## Series Roadmap (naming only, future work)

Repo folder (`lessons/<name>/`, snake_case) → portfolio slug (kebab-case),
in the blog's complexity order:

| # | Repo folder | Portfolio slug | Architecture | Status |
|---|---|---|---|---|
| 1 | `naive_rag` | `naive-rag` | Naive (Standard) RAG | **Authored (Phase A done), not yet published** |
| 2 | `hybrid_rag` | `hybrid-rag` | Hybrid (dense + sparse) RAG | **Authored (Phase A done), not yet published** |
| 3 | `graph_rag` | `graph-rag` | Graph RAG (knowledge graphs, multi-hop) - note: distinct from the existing `pggraph` course, which teaches the Postgres extension, not the RAG architecture; scope this to avoid duplicating pggraph's content when we get there | **Plan drafted, syllabus not yet approved** |
| 4 | `corrective_rag` | `corrective-rag` | Corrective RAG (CRAG) | **Authored (Phase A done), not yet published** |
| 5 | `agentic_rag` | `agentic-rag` | Agentic RAG | **Plan drafted, syllabus not yet approved** |
| 6 | `multimodal_rag` | `multimodal-rag` | Multimodal RAG | **Plan drafted, syllabus not yet approved** |
| 7 | `adaptive_rag` | `adaptive-rag` | Adaptive RAG | **Plan drafted (series closer - do not author until courses 2-5 are done)** |

This table is the one to keep updated as each course ships (see
"Persisting This Plan for Future Courses" below).

Advanced RAG and Modular RAG (the blog's other two "beginner tier" entries)
are meta-categories (optimization stages / composability pattern) rather
than standalone techniques - likely folded into the Naive RAG course's
intermediate tier and revisited across the series rather than getting their
own course. Revisit this when planning course 2.

## Persisting This Plan for Future Courses

Since the Series Roadmap above spans 7 planned courses and only the first
is built now, this plan lives inside the content repo itself (not just a
throwaway session plan file) so course 2+ can start from the same
roadmap/spec conventions instead of re-deriving them:

- Lives at `/home/nolan/Documents/Projects/ai-agent-engineering/docs/RAG-SERIES-PLAN/`
  (the repo's first `docs/` content, one file per phase plus this
  overview).
- Update the Series Roadmap table's status column (e.g. Naive RAG →
  "Published") as each course finishes.

## Shared Strategy Protocol (cross-course convention)

Added after a pedagogical review of courses 2-7's draft syllabi against
the finished `naive_rag` course. Every course's refactor lesson (always
numbered around 23, `ingest()`/`ask()`) should converge on the same
minimal shape, so `adaptive_rag` Lesson 21 ("wiring in real Advanced-tier
implementations from courses 2-5") is actually wiring in five things that
already fit together, not reconciling five bespoke signatures written a
year apart with no shared contract.

```python
class Strategy(Protocol):
    def ingest(self, docs: list[Path]) -> object: ...   # returns opaque State
    def ask(self, query: str, state: object, k: int = 2) -> str: ...
```

- `ingest()` takes the fixture folder and returns whatever state that
  course's retrieval needs (a `chromadb.Collection`, a `(bm25_index,
  chroma_collection)` tuple, a graph + collection pair, a grader +
  collection pair, ...) - the state's *type* is course-specific, the
  two-function boundary isn't.
- `ask()` always takes the query, that state, and `k`, and always returns
  the final answer string with citations folded in (not a separate return
  value), matching every course's existing README convention.
- `naive_rag`'s already-written Lesson 23 (`ingest(notes_dir, chroma_client)
  -> Collection`, `ask(query, collection, k=2) -> str`) is close enough to
  serve as the reference implementation as-is - it's finished and verified
  against the real API, so it isn't being rewritten for this. Courses 2-7
  should match this shape deliberately from the start rather than drift
  further from it the way five independently-drafted signatures would.
- Each course's own Lesson 23 README should say explicitly which of its
  own ingredients (sparse index, graph, grader, tool registry) live inside
  its `State`, so `adaptive_rag` Lesson 21 can import and compose them
  without reading five full implementations first.

## Eval-Methodology Caveat (cross-course convention)

Also added after the same review: every course's "minimal evaluation"
lesson (always numbered around 17, precision@k on a small hand-labeled
question set) needs to teach the limits of that method as content, not
bury it as a one-line caveat. `naive_rag` Lesson 17 now does this - see
its README's "Why this doesn't generalize (yet)" section - covering why a
handful of questions can't distinguish real improvement from noise, and
why tuning a hyperparameter (a threshold, an RRF `k`, a routing rule)
against the same tiny set you report your final score on is
train/test contamination, not evaluation. Courses 2-7's own Lesson 17
should reference that section rather than re-deriving it, and each
course's Lesson 11/14-equivalent "tuning" lesson (RRF `k` in `hybrid_rag`,
traversal depth in `graph_rag`, rewrite strategy in `corrective_rag`,
routing rules in `adaptive_rag`) should say explicitly whether the tuning
in that lesson is safe (tuned against a different signal, the way
`naive_rag` L14's threshold came from L3's raw score gap, not from the L17
labeled set) or is the deliberately-flagged contaminated case.
