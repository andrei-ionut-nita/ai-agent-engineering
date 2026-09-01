# Phase B: Publish `naive_rag` to the portfolio

**Status: not started.** Gate: only start once the user has
reviewed/skimmed the finished `naive_rag` course (see
[`phase-a-authoring.md`](./phase-a-authoring.md)) and explicitly says to
proceed. Don't reimplement any of the `/write-course` pipeline here; this
plan's job in Phase B is just to invoke it correctly and track it through
to done.

## To-Do List

- [ ] Run `/write-course` (portfolio) end to end for `naive_rag` →
      `naive-rag`, through its own approval gates
- [ ] Verify the published course: `npm run check:types` /
      `check:tokens` / `lint:css` / `build`, source-link integrity check,
      `npm run preview` visit to `/learning/naive-rag/` and one lesson

## Published Page Mockup (`andreinita.co/learning/naive-rag/`)

```
┌─────────────────────────────────────────────────────────────┐
│  ← Learning                                                  │
│                                                               │
│  Naive RAG: Building the Baseline from Scratch               │
│  A linear, one-concept-per-lesson path through the simplest  │
│  RAG architecture, from your first embedding call to a       │
│  complete, capstone Q&A app.                                 │
│                                                               │
│  [ View source on GitHub ↗ ]        ← SourceBanner           │
│                                                               │
│  Prerequisites: none beyond a Gemini API key                 │
│  Model: Gemini (GOOGLE_API_KEY, same as every other course)  │
│                                                               │
│  ── Beginner ──────────────────────────────────────────────  │
│  Hand-rolled RAG, one piece at a time. No frameworks yet.    │
│   01  What Is Naive RAG?                              [gh]   │
│   02  Your First Embedding                            [gh]   │
│   03  Cosine Similarity by Hand                        [gh]   │
│   ...                                                        │
│   09  Beginner Checkpoint: Folder Q&A            ◆     [gh]   │
│                                                               │
│  ── Intermediate ──────────────────────────────────────────  │
│  Where naive RAG breaks, and the fixes that keep it naive.  │
│   10  Chunk Size and Overlap                           [gh]   │
│   ...                                                        │
│   18  Intermediate Checkpoint: Notes Search      ◆     [gh]   │
│                                                               │
│  ── Advanced ──────────────────────────────────────────────  │
│  Graduating the hand-rolled store, and a capstone.           │
│   19  Where Linear Scan Breaks Down                    [gh]   │
│   ...                                                        │
│   25  Capstone: A Complete Naive RAG App         ◆     [gh]   │
│   26  Where Naive RAG Hits a Wall                      [gh]   │
└─────────────────────────────────────────────────────────────┘
   [gh] = per-row GitHub source-link icon      ◆ = checkpoint lesson
```

This follows the exact `langchain-and-agents/index.astro` reference
layout `/write-course` already uses - no new page design, this mockup is
just to confirm the tier descriptions and lesson list read well before
26 lesson pages get generated from them.

## Execution Steps

1. Confirm with the user that Phase A is approved and they want
   publishing to start now (do not assume - this is a separate gate from
   Phase A's own lesson-writing gate).
2. Invoke the existing `/write-course` skill (`portfolio:write-course`)
   with:
   - `sourceSlug`: `naive_rag`
   - `slug`: `naive-rag`
   - `topic`: `Retrieval` (existing catalog value, no catalog edit needed)
   - `title`: "Naive RAG: Building the Baseline from Scratch" (from the
     Course 1 Spec in `phase-a-authoring.md`)
3. Let the skill run its own phases end to end: metadata drafting, the
   lesson inventory gate, data-model file creation, syllabus + lesson
   `.astro` pages, catalog registration, build/verify, and staging. Answer
   any gates it raises; don't skip or shortcut them.
4. Optional Phase 7 (`/generate-og-image`) only if the user supplies a
   source image - not blocking, skip if none is provided.
5. Run the skill's own Phase 8 verification (see Verification below) and
   fix anything it flags before considering Phase B done.
6. Once verified, update the Series Roadmap table in
   [`../README.md`](../README.md): `naive_rag` status → "Published".
7. Report back to the user with the live/staged URL
   (`/learning/naive-rag/`) and confirm whether they want it
   committed/pushed (per this repo's convention, don't commit or push
   without being explicitly asked).

## Verification

The `/write-course` skill's own Phase 8 (`npm run check:types`,
`check:tokens`, `lint:css`, `build`) plus its source-link integrity check
and a manual `npm run preview` visit to `/learning/naive-rag/` and one
lesson page.
