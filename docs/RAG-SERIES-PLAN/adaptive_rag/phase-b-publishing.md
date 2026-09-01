# Phase B: Publish `adaptive_rag` to the portfolio

**Status: not started.** Gate: only start once Phase A
([`phase-a-authoring.md`](./phase-a-authoring.md)) is complete and the
user has reviewed/skimmed the finished course. Mirrors
[`../naive_rag/phase-b-publishing.md`](../naive_rag/phase-b-publishing.md)
exactly - only the course-specific values differ.

This is the series' final course - once it's published, revisit the
portfolio's `rag-fundamentals` overview page (mentioned in the series
`README.md`'s Context section) to check whether it should now cross-link
to all seven hands-on courses rather than however many existed when it
was last touched.

## To-Do List

- [ ] Run `/write-course` (portfolio) end to end for `adaptive_rag` →
      `adaptive-rag`, through its own approval gates
- [ ] Verify the published course: `npm run check:types` /
      `check:tokens` / `lint:css` / `build`, source-link integrity check,
      `npm run preview` visit to `/learning/adaptive-rag/` and one lesson
- [ ] Check whether `rag-fundamentals`'s overview page should link to all
      seven hands-on courses now that the series is complete

## Execution Steps

1. Confirm with the user that Phase A is approved and they want
   publishing to start now.
2. Invoke the existing `/write-course` skill (`portfolio:write-course`)
   with:
   - `sourceSlug`: `adaptive_rag`
   - `slug`: `adaptive-rag`
   - `topic`: `Retrieval` (existing catalog value, no catalog edit needed)
   - `title`: "Adaptive RAG: Routing Each Question to the Right
     Strategy" (from the Course 7 Spec in `phase-a-authoring.md`)
3. Let the skill run its own phases end to end: metadata drafting, the
   lesson inventory gate, data-model file creation, syllabus + lesson
   `.astro` pages, catalog registration, build/verify, and staging.
4. Optional `/generate-og-image` only if the user supplies a source
   image - not blocking.
5. Run the skill's own Phase 8 verification (see Verification below) and
   fix anything it flags before considering Phase B done.
6. Once verified, update the Series Roadmap table in
   [`../README.md`](../README.md): `adaptive_rag` status → "Published".
7. Check whether `rag-fundamentals`'s overview page needs updated
   cross-links now that all seven courses are live.
8. Report back to the user with the live/staged URL
   (`/learning/adaptive-rag/`) and confirm whether they want it
   committed/pushed.

## Verification

The `/write-course` skill's own Phase 8 (`npm run check:types`,
`check:tokens`, `lint:css`, `build`) plus its source-link integrity check
and a manual `npm run preview` visit to `/learning/adaptive-rag/` and one
lesson page.
