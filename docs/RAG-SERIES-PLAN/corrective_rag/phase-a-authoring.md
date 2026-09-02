# Phase A: Author the `corrective_rag` course

**Status: Phase A complete.** All 26 lessons are written and verified
against the real `GOOGLE_API_KEY`. Mirrors
[`../naive_rag/phase-a-authoring.md`](../naive_rag/phase-a-authoring.md)'s
structure and conventions exactly - only the content differs. Phase B
(portfolio publishing) is not started, awaiting explicit user go-ahead.

## To-Do List

- [x] Get user approval on this syllabus before writing any files -
      approved after an MIT-professor-style technical review; five fixes
      applied (paper citation + named simplifications in L1, binary
      grading in Beginner with the three-way bucket deferred to L12,
      L6-7 marked as a simplification of the paper's actual "incorrect"
      branch, L22 reframed from optional extra to that real branch, L17
      adds an end-to-end answer-quality check alongside precision@k)
- [x] Lesson 23's `ingest()`/`ask()` implements the series' shared
      `Strategy` protocol (`docs/RAG-SERIES-PLAN/README.md`): `ingest(docs)
      -> State` where `State` here is `(chroma_collection, grader)`,
      `ask(query, state, k) -> str`. Said explicitly in that lesson's
      README what lives inside `State` (`CorrectiveState.collection` and
      `.grader`), so `adaptive_rag` L21 can wire this in without reading
      the full implementation.
- [x] Lesson 17 references `naive_rag` L17's "Why this doesn't generalize
      (yet)" section (sample-size limits, tune/eval contamination) instead
      of re-deriving it. Lesson 14 (rewriting strategies) states explicitly
      that its decompose/broaden/narrow heuristic was tuned against
      Lessons 6-12's hand-inspected failure shapes, a held-out signal
      separate from L17's labeled set, not against that set itself.
- [x] Lesson 16 (failure modes) treats grader/generator shared-bias
      circularity as its primary content: a deliberately fabricated,
      internally-consistent but false passage was empirically verified
      to get graded "correct" by the same model that then generates a
      confidently wrong answer from it, both wrong the same way. Shown,
      not just asserted - see the lesson's own README and verified output.
- [x] Lesson 24 (FastAPI wrapper) stays a short recipe reusing
      `naive_rag` L24's pattern almost verbatim rather than re-teaching
      FastAPI from scratch - kept brief, defers depth to Lesson 16.
- [x] Decided `lessons/corrective_rag/fixtures/` needs its own copy of
      `naive_rag`'s five notes, with one small edit: `bookshelf.md`'s
      "the weather station's Raspberry Pi" became "Project Aurora's
      Raspberry Pi" so a correction's generated answer can actually name
      the project once retrieval finds the right chunk. Empirically
      verified (real embedding calls) that the question "Project
      Aurora's Raspberry Pi writes sensor readings to a SQLite file on
      its SD card. Where does that Raspberry Pi physically live in the
      house?" makes naive top-1 retrieval confidently return
      `weather-station.md` (score ~0.77, topically spot-on, factually
      wrong) over the actually-correct `bookshelf.md` (score ~0.75) -
      exactly the "looks relevant, is wrong" shape this course needed,
      not just a low-similarity miss. No additional fixture notes were
      needed beyond this one wording edit.
- [x] Scaffold `lessons/corrective_rag/` structure (tier folders, lesson
      folders, course-level `README.md`)
- [x] Write Beginner tier (9 lessons): grading retrieved chunks by hand,
      filtering, query rewriting, re-retrieval
- [x] Write Intermediate tier (9 lessons): strip-level grading,
      confidence buckets, persistence, rewriting strategies, failure
      modes, minimal eval, checkpoint
- [x] Write Advanced tier (8 lessons): cost of grading at scale, a
      cheap pre-filter, bounded correction loops, an optional pluggable
      external-search step, refactor, service wrapper, capstone, series
      bridge lesson
- [x] No new dependency needed - confirmed, reuses `google-genai`,
      `chromadb`, and `fastapi`, all already in `pyproject.toml`.
      `pyproject.toml` was not touched.
- [x] Added the `corrective_rag` course bullet to the repo root `README.md`
- [x] Every lesson's `lesson.py` was run against the real `GOOGLE_API_KEY`
      and its output matches its README's "Expected output" section.

## Course 4 Spec: Corrective RAG

- **Repo folder**: `lessons/corrective_rag/`
- **Portfolio slug**: `corrective-rag`
- **Title**: "Corrective RAG: Grading and Fixing Retrieval Before You Generate"
- **Topic** (portfolio): `Retrieval` (existing value, no catalog edit
  needed)
- **Model**: Gemini (`GOOGLE_API_KEY`), used for retrieval grading (a
  prompted relevance classifier: correct / ambiguous / incorrect), query
  rewriting, and generation - same account/API surface as every prior
  course.
- **New dependency**: none expected. `chromadb` is reused from
  `naive_rag`'s Advanced tier for the vector store.
- **Relationship to prior courses**: this course's premise is the
  specific failure `naive_rag` Lesson 14/22 demonstrated - retrieval that
  returns a confident top-k match which is actually irrelevant, with
  nothing in the pipeline aware of that. Lesson 2 recaps that failure
  directly before introducing grading as the fix.
- **Grounding and named simplifications**: this course teaches the
  mechanism from Yan et al. 2024, "Corrective Retrieval Augmented
  Generation" (arXiv:2401.15884) - a retrieval evaluator that grades each
  chunk's confidence (correct / ambiguous / incorrect), knowledge
  refinement via decompose-then-recompose on "correct" chunks, and
  external web search as the fallback for "incorrect" ones. Lesson 1
  cites the paper and names two deliberate simplifications up front, so
  a student who later reads the paper isn't confused by the difference:
  (1) Beginner's rewrite-and-re-retrieve loop (L6-7) queries the *same*
  internal corpus, where the paper's actual "incorrect" branch goes to
  external web search (built properly in L22, reframed below as
  implementing that branch, not as an optional extra); (2) Beginner
  grades chunks as a binary relevant/not-relevant call, deferring the
  paper's three-way correct/ambiguous/incorrect confidence bucketing
  to Intermediate L12, once the strip-level refinement it depends on
  exists.

### Lesson breakdown (26 lessons across 3 tiers, draft)

**Beginner - grading and correcting retrieval by hand (9 lessons)**
1. What Corrective RAG is: retrieval can silently return irrelevant chunks, and generation never finds out
2. Recap: watching naive retrieval return a confidently-wrong top-k chunk (reusing `naive_rag`'s threshold/metadata-filtering failure demos)
3. Grading a single retrieved chunk: prompting Gemini for a binary relevant / not-relevant call against the query (the paper's full three-way correct/ambiguous/incorrect grading arrives in Intermediate L12, once strip-level refinement exists to act on "ambiguous")
4. Grading all top-k chunks: a batch relevance-grading step run right after retrieval
5. Filtering: dropping chunks graded not-relevant before they ever reach generation
6. Query rewriting: prompting Gemini to rephrase the query when every chunk is graded not-relevant (a simplification - the paper's actual response to a low-confidence grade is external web search, built properly in Advanced L22; this internal rewrite loop is the easier version to build first)
7. Re-retrieval with the rewritten query, against the same internal corpus
8. End-to-end: retrieve → grade → filter/rewrite → re-retrieve → generate, one script
9. Beginner checkpoint: a CLI Q&A that visibly self-corrects when the first retrieval attempt misses

**Intermediate - making correction precise and bounded (9 lessons)**
10. Grading granularity: whole-chunk grading vs. splitting a chunk into strips and grading each strip
11. Recomposing context from only the relevant strips, instead of keeping or discarding whole chunks
12. Upgrading L3's binary grade to the paper's full three-way confidence buckets (correct / ambiguous / incorrect), each mapped to a distinct action: correct → strip-level refinement only, incorrect → discard, ambiguous → refinement plus flag for query rewriting
13. Persisting grading results alongside the vector store so identical chunks aren't re-graded every run
14. Query rewriting strategies: broadening, narrowing, and decomposing into sub-questions
15. Prompting for grounded answers that disclose when a correction happened and why
16. Failure modes, foregrounding grader/generator circularity: the grader shares the generator's model family and can share its blind spots, so a confidently-wrong grade goes uncaught the same way a confidently-wrong retrieval did in `naive_rag` - shown by deliberately constructing a question where the grader mis-scores a chunk the same way the generator would have misread it; also rewrite loops that don't converge
17. Minimal evaluation: precision@k before vs. after correction on a labeled question set, plus a small end-to-end answer-quality check (does the graded/corrected pipeline's final answer actually improve on the questions where naive retrieval was confidently wrong, not just its retrieval precision) - references `naive_rag` L17's "Why this doesn't generalize (yet)" section per the To-Do List, and makes explicit that precision@k alone doesn't prove this course's L1 premise, generation quality has to be checked directly
18. Intermediate checkpoint: the notes-search assistant with a visible "retrieval was corrected" indicator and citations

**Advanced - making correction affordable, and a capstone (8 lessons)**
19. Where grading every chunk on every query gets expensive at scale
20. A cheap pre-filter (similarity-score threshold) before invoking the LLM grader, to cut grading calls
21. Bounding correction loops: a max-rewrite-attempts guard before falling back to "I don't know"
22. External web search as the paper's actual "incorrect" branch: replacing L6-7's internal rewrite-and-retry with the real corrective action from Yan et al. 2024, so the course closes the gap it named in L1 (implementation stays pluggable/stubbed - no required external API key - but the lesson is explicit that this, not L6-7, is what "Corrective RAG" means in the literature)
23. Refactoring the pipeline into reusable functions (`ingest()`, `grade()`, `correct()`, `ask()`)
24. Wrapping it as a small callable service (FastAPI, matching `naive_rag` Lesson 24's pattern)
25. Advanced capstone: a complete corrective RAG service with grading, bounded correction, and citations
26. Where Corrective RAG hits a wall - a short bridge lesson naming the failure modes that motivate Agentic RAG (sets up course 5, no code)

Numbers/exact count may shift once READMEs are drafted, same caveat as
prior courses' syllabi.

## File Tree (`lessons/corrective_rag/`, draft)

```
lessons/corrective_rag/
├── README.md
├── 01_beginner/
│   ├── 01_what_is_corrective_rag/
│   ├── 02_where_naive_retrieval_is_confidently_wrong/
│   ├── 03_grading_a_retrieved_chunk/
│   ├── 04_grading_all_top_k_chunks/
│   ├── 05_filtering_out_incorrect_chunks/
│   ├── 06_query_rewriting/
│   ├── 07_re_retrieval_with_the_rewritten_query/
│   ├── 08_end_to_end_corrective_qa/
│   └── 09_beginner_checkpoint_project/
├── 02_intermediate/
│   ├── 10_strip_level_grading/
│   ├── 11_recomposing_context_from_relevant_strips/
│   ├── 12_confidence_buckets_and_actions/
│   ├── 13_persisting_grading_results/
│   ├── 14_query_rewriting_strategies/
│   ├── 15_prompting_for_disclosed_corrections/
│   ├── 16_failure_modes_of_grading_and_rewriting/
│   ├── 17_minimal_evaluation_before_vs_after_correction/
│   └── 18_intermediate_checkpoint_project/
├── 03_advanced/
│   ├── 19_where_per_chunk_grading_gets_expensive/
│   ├── 20_a_cheap_pre_filter_before_grading/
│   ├── 21_bounding_correction_loops/
│   ├── 22_external_web_search_as_the_incorrect_branch/
│   ├── 23_refactoring_into_ingest_grade_correct_ask/
│   ├── 24_wrapping_it_as_a_service/
│   ├── 25_advanced_capstone_project/
│   └── 26_where_corrective_rag_hits_a_wall/
└── fixtures/
```

## Execution Steps (draft, mirrors `naive_rag`)

1. Present this syllabus to the user and get approval before writing any
   lesson files.
2. Confirm or adjust the fixture/question set so it produces the
   confidently-wrong-retrieval failure this course is built around (see
   To-Do List above).
3. Scaffold `lessons/corrective_rag/` matching `lessons/naive_rag/`'s
   structure exactly.
4. Write the lessons tier by tier, spot-checking `uv run python
   lessons/corrective_rag/<tier>/<lesson>/lesson.py` against a real
   `GOOGLE_API_KEY` as each tier completes.
5. Update repo-wide files:
   - Root `README.md`: add the `corrective_rag` course bullet.
   - `pyproject.toml`: only touch if a lesson ends up needing something
     beyond `google-genai`/`chromadb` (not expected).
6. Run `uv sync` and do a final full read-through pass of the new course
   folder.

## Verification

Every lesson's `lesson.py` actually runs and produces the output
documented in its README's "Expected output" section. Lesson 17's
precision@k comparison should show correction clearly improving precision
on questions where naive retrieval was confidently wrong - if it doesn't,
the fixture/question set likely needs adjusting so the lesson's point
actually lands.
