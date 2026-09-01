# Phase A: Author the `hybrid_rag` course

**Status: complete.** All 26 lessons authored and verified against the
real Gemini API.

Repo: `/home/nolan/Documents/Projects/ai-agent-engineering`, mirroring
[`../naive_rag/phase-a-authoring.md`](../naive_rag/phase-a-authoring.md)'s
structure and conventions exactly - only the content differs.

## To-Do List

- [x] Get user approval on this syllabus before writing any files
- [x] Lesson 23's `ingest()`/`ask()` implements the series' shared
      `Strategy` protocol (`docs/RAG-SERIES-PLAN/README.md`): `ingest(docs)
      -> State` where `State` (`HybridState`) holds a `chromadb.Collection`
      and a `BM25Okapi` index, `ask(query, state, k) -> str`.
- [x] Lesson 17 references `naive_rag` L17's "Why this doesn't generalize
      (yet)" section instead of re-deriving it. Lesson 11 (tuning RRF's
      `k`) is explicit that it deliberately tunes against the same
      labeled set L17 scores, the flagged-contaminated case, using a
      synthetic example (not the real corpus) to demonstrate `k`'s actual
      effect since this course's six real documents don't disagree
      between dense and sparse enough to show it directly.
- [x] Lesson 24 (FastAPI wrapper) stays a short recipe reusing
      `naive_rag` L24's pattern almost verbatim.
- [x] Designed `lessons/hybrid_rag/fixtures/notes/` - six fresh notes
      (home network, espresso machine, houseplants, bike maintenance, 3D
      printer, plus a confusable second router note added during
      authoring so dense retrieval has a genuine near-miss to make, not
      just a thin-margin win) with both lexical gotchas (bare IDs, model
      numbers, product names) and semantic gotchas (paraphrases avoiding
      the answer's technical vocabulary).
- [x] Scaffolded `lessons/hybrid_rag/` structure (tier folders, lesson
      folders, course-level `README.md`)
- [x] Wrote Beginner tier (9 lessons)
- [x] Wrote Intermediate tier (9 lessons)
- [x] Wrote Advanced tier (8 lessons)
- [x] Added `rank_bm25` to `pyproject.toml`; ran `uv sync`
- [x] Added the `hybrid_rag` course bullet to the repo root `README.md`
- [x] Spot-checked every lesson's `lesson.py` against the real
      `GOOGLE_API_KEY` while authoring; all 26 pass `py_compile`

## Course 2 Spec: Hybrid RAG

- **Repo folder**: `lessons/hybrid_rag/` (new, top-level, sibling to
  `naive_rag` and the other course folders)
- **Portfolio slug**: `hybrid-rag`
- **Title**: "Hybrid RAG: Combining Dense and Sparse Retrieval"
- **Topic** (portfolio): `Retrieval` (existing value, no catalog edit
  needed)
- **Model**: Gemini, same as `naive_rag` (`GOOGLE_API_KEY`,
  `google-genai`'s embedding + chat endpoints) - the dense half of this
  course is a direct continuation of `naive_rag`'s Beginner tier, so no
  new account/API surface is introduced there.
- **New dependency**: `rank_bm25` (pure Python, no server - keeps this
  course as light-setup as `naive_rag`) for the sparse half. `chromadb`
  is reused in the Advanced tier for the dense half, same as `naive_rag`.
- **Relationship to `naive_rag`**: this course assumes the reader has
  either taken `naive_rag` or otherwise knows what "dense retrieval" and
  "cosine similarity" mean - Lesson 2 is a compressed recap, not a full
  re-teach. Hybrid RAG's whole premise (dense retrieval alone misses
  exact keyword/ID matches) is only motivating if the reader already
  understands the dense-only baseline.

### Lesson breakdown (26 lessons across 3 tiers, draft)

**Beginner - sparse retrieval by hand, then fusing it with dense (9 lessons)**
1. What Hybrid RAG is: the specific gap dense-only retrieval leaves open
2. Recap: dense retrieval in one script (reusing the `naive_rag` pattern - embed, cosine similarity, top-k)
3. Keyword search by hand: raw term-frequency scoring
4. TF-IDF by hand: downweighting common words, upweighting rare ones
5. BM25 by hand: TF-IDF's length-normalized, saturating cousin
6. Dense vs. sparse on the same queries: cases where each one wins and the other misses entirely - and *why*, not just that it happens: embedding models undertrain on rare tokens (exact IDs, model numbers, acronyms), so a query and its answer can be nearby in meaning but far apart in embedding space, while BM25 only ever sees literal token overlap and doesn't care about meaning at all
7. Naive score combination: a weighted sum of normalized dense + sparse scores, and why the weight is fragile
8. Reciprocal Rank Fusion (RRF): combining two rankings without needing comparable scores or a tuned weight
9. Beginner checkpoint: a hybrid search CLI over the course fixtures, returning RRF-fused top-k

**Intermediate - making the fusion robust and multi-document (9 lessons)**
10. Normalizing scores before fusion (min-max / z-score) when you do need a weighted blend instead of RRF
11. Tuning RRF's `k` constant and its effect on how much low-ranked results matter
12. Metadata-aware hybrid retrieval: source/tag filters applied identically to both retrievers before fusing
13. Persisting both indexes to disk (the sparse index and the dense vector store) instead of rebuilding every run
14. When sparse wins: exact IDs, model numbers, acronyms, rare proper nouns that embeddings blur together
15. When dense wins: paraphrases and synonyms with zero shared keywords
16. Failure modes of hybrid retrieval: cases where fusion still misses because neither retriever individually ranked the right chunk highly enough
17. Minimal evaluation: precision@k for dense-only vs. sparse-only vs. hybrid, side by side on the same labeled question set
18. Intermediate checkpoint: the `naive_rag` notes-search assistant upgraded to hybrid retrieval, citations intact

**Advanced - graduating both retrievers, and a capstone (8 lessons)**
19. Where hand-rolled BM25 (and linear-scan dense search) break down at scale
20. Introducing `rank_bm25` as a drop-in replacement for the hand-rolled sparse index
21. Introducing `chromadb` for the dense half, `rank_bm25` for the sparse half, fused with RRF
22. Alpha-blended fusion as an alternative to RRF, now with real (not hand-rolled) retrievers
23. Refactoring the pipeline into reusable functions (`ingest()`, `ask()`)
24. Wrapping it as a small callable service (FastAPI, matching `naive_rag` Lesson 24's pattern)
25. Advanced capstone: a complete hybrid RAG service with citations and documented limitations
26. Where hybrid RAG hits a wall - a short bridge lesson naming the failure modes that motivate Graph/Corrective/Agentic RAG (sets up course 3, no code)

Numbers/exact count may shift once READMEs are drafted, same caveat as
`naive_rag`'s syllabus - the tier shape and rough count is the target,
not a hard requirement.

## File Tree (`lessons/hybrid_rag/`, draft)

```
lessons/hybrid_rag/
├── README.md                                    # course index (tier tables)
├── 01_beginner/
│   ├── 01_what_is_hybrid_rag/
│   ├── 02_dense_retrieval_recap/
│   ├── 03_keyword_search_by_hand/
│   ├── 04_tfidf_by_hand/
│   ├── 05_bm25_by_hand/
│   ├── 06_dense_vs_sparse_head_to_head/
│   ├── 07_naive_score_combination/
│   ├── 08_reciprocal_rank_fusion/
│   └── 09_beginner_checkpoint_project/          # hybrid search CLI
├── 02_intermediate/
│   ├── 10_normalizing_scores_before_fusion/
│   ├── 11_tuning_rrf_k/
│   ├── 12_metadata_aware_hybrid_retrieval/
│   ├── 13_persisting_both_indexes/
│   ├── 14_where_sparse_wins/
│   ├── 15_where_dense_wins/
│   ├── 16_failure_modes_of_hybrid_retrieval/
│   ├── 17_minimal_evaluation_dense_vs_sparse_vs_hybrid/
│   └── 18_intermediate_checkpoint_project/      # upgraded notes-search assistant
├── 03_advanced/
│   ├── 19_where_hand_rolled_retrieval_breaks_down/
│   ├── 20_introducing_rank_bm25/
│   ├── 21_repointing_at_chromadb_and_rank_bm25/
│   ├── 22_alpha_blended_fusion/
│   ├── 23_refactoring_into_ingest_and_ask/
│   ├── 24_wrapping_it_as_a_service/
│   ├── 25_advanced_capstone_project/            # full hybrid RAG service
│   └── 26_where_hybrid_rag_hits_a_wall/         # bridge to course 3, no code
└── fixtures/                                    # notes with both lexical and semantic gotchas
```

Every leaf lesson folder gets `README.md` + `lesson.py`, same shape as
`naive_rag`.

## Execution Steps (draft, mirrors `naive_rag`)

1. Present this syllabus to the user and get approval before writing any
   lesson files.
2. Design and write `lessons/hybrid_rag/fixtures/` - the fixture design
   is the one genuinely new piece of groundwork this course needs (see
   To-Do List above); everything else follows `naive_rag`'s conventions.
3. Scaffold `lessons/hybrid_rag/` (tier folders, lesson folders,
   course-level `README.md`), matching `lessons/naive_rag/`'s structure
   exactly.
4. Write the lessons tier by tier, spot-checking `uv run python
   lessons/hybrid_rag/<tier>/<lesson>/lesson.py` against a real
   `GOOGLE_API_KEY` as each tier completes.
5. Update repo-wide files:
   - `pyproject.toml`: add `rank_bm25`.
   - Root `README.md`: add the `hybrid_rag` course bullet (18th course).
6. Run `uv sync` and do a final full read-through pass of the new course
   folder.

## Verification

Every lesson's `lesson.py` actually runs and produces the output
documented in its README's "Expected output" section; `uv sync` succeeds
after the `rank_bm25` dependency add; the precision@k comparison in
Lesson 17 should show hybrid ≥ both dense-only and sparse-only on the
labeled question set - if it doesn't, the fixture set or labeled
questions likely need adjusting so the lesson's point actually lands.

Confirmed: all 26 lesson folders have both `README.md` and `lesson.py`,
all pass `py_compile`, `uv sync` succeeds with `rank_bm25` installed, and
every lesson was run against the live Gemini API while authoring.
Lesson 17's precision@1 came out dense-only 9/11, sparse-only 9/11,
hybrid RRF 10/11, hybrid strictly ahead of both, on an eleven-question
set that includes Lesson 16's known-hard case (which hybrid still
misses, by design, not smoothed over).
