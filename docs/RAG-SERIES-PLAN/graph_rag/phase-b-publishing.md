# Phase B: Publish `graph_rag` to the portfolio

**Status: not started.** Gate: only start once Phase A
([`phase-a-authoring.md`](./phase-a-authoring.md)) is complete and the
user has reviewed/skimmed the finished course. Mirrors
[`../naive_rag/phase-b-publishing.md`](../naive_rag/phase-b-publishing.md)
exactly - only the course-specific values differ.

## To-Do List

- [ ] Run `/write-course` (portfolio) end to end for `graph_rag` →
      `graph-rag`, through its own approval gates
- [ ] Verify the published course: `npm run check:types` /
      `check:tokens` / `lint:css` / `build`, source-link integrity check,
      `npm run preview` visit to `/learning/graph-rag/` and one lesson

## Execution Steps

1. Confirm with the user that Phase A is approved and they want
   publishing to start now.
2. Invoke the existing `/write-course` skill (`portfolio:write-course`)
   with:
   - `sourceSlug`: `graph_rag`
   - `slug`: `graph-rag`
   - `topic`: `Retrieval` (existing catalog value, no catalog edit needed)
   - `title`: "Graph RAG: Answering Multi-Hop Questions with a Knowledge
     Graph" (from the Course 3 Spec in `phase-a-authoring.md`)
3. Let the skill run its own phases end to end: metadata drafting, the
   lesson inventory gate, data-model file creation, syllabus + lesson
   `.astro` pages, catalog registration, build/verify, and staging.
4. Optional `/generate-og-image` only if the user supplies a source
   image - not blocking.
5. Run the skill's own Phase 8 verification (see Verification below) and
   fix anything it flags before considering Phase B done.
6. Once verified, update the Series Roadmap table in
   [`../README.md`](../README.md): `graph_rag` status → "Published".
7. Report back to the user with the live/staged URL
   (`/learning/graph-rag/`) and confirm whether they want it
   committed/pushed.

## Verification

The `/write-course` skill's own Phase 8 (`npm run check:types`,
`check:tokens`, `lint:css`, `build`) plus its source-link integrity check
and a manual `npm run preview` visit to `/learning/graph-rag/` and one
lesson page.
