# Course index

A linear, one-concept-per-lesson path through Hybrid RAG, dense
(embedding) retrieval combined with sparse (keyword) retrieval, built
from scratch before graduating to real libraries: no LangChain, no
LlamaIndex, direct calls to Google's Gemini API (`google-genai`), hand-
rolled BM25, then `rank_bm25` and `chromadb`. Do these in order, top to
bottom, each lesson folder has a `README.md` (read first) and a
`lesson.py` (run second). Don't move to the next lesson until the
current one's checkpoint questions feel solid.

This is course 2 in a series organized by RAG architecture (mirroring
[andreinita.co/learning/rag-fundamentals](https://andreinita.co/learning/rag-fundamentals/)'s
map of nine architectures). It assumes you've done
[`lessons/naive_rag/`](../naive_rag/) (course 1) or otherwise already
know what dense retrieval is, cosine similarity, embeddings, top-`k`,
Lesson 2 here is a compressed recap, not a full re-teach.

Setup: `GOOGLE_API_KEY` in a `.env` file at the project root (get a free
key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)),
no Docker, no database, no extra account. Then
`uv run python lessons/hybrid_rag/<NN>_<name>/lesson.py` from the
project root.

## Beginner: sparse retrieval by hand, then fusing it with dense

| # | Lesson | Concept |
|---|--------|---------|
| 01 | [what_is_hybrid_rag](01_beginner/01_what_is_hybrid_rag/) | The specific gap dense-only retrieval leaves open |
| 02 | [dense_retrieval_recap](01_beginner/02_dense_retrieval_recap/) | Dense retrieval in one script, recapped from `naive_rag` |
| 03 | [keyword_search_by_hand](01_beginner/03_keyword_search_by_hand/) | Raw term-frequency scoring, no embeddings |
| 04 | [tfidf_by_hand](01_beginner/04_tfidf_by_hand/) | Downweighting common words, upweighting rare ones |
| 05 | [bm25_by_hand](01_beginner/05_bm25_by_hand/) | TF-IDF's length-normalized, saturating cousin |
| 06 | [dense_vs_sparse_head_to_head](01_beginner/06_dense_vs_sparse_head_to_head/) | Both retrievers, same ten questions, opposite blind spots |
| 07 | [naive_score_combination](01_beginner/07_naive_score_combination/) | A weighted sum of normalized scores, and why the weight is fragile |
| 08 | [reciprocal_rank_fusion](01_beginner/08_reciprocal_rank_fusion/) | RRF: combining rankings without scores or a tuned weight |
| 09 | [beginner_checkpoint_project](01_beginner/09_beginner_checkpoint_project/) | **Checkpoint:** Hybrid Search CLI |

## Intermediate: making the fusion robust and multi-document

| # | Lesson | Concept |
|---|--------|---------|
| 10 | [normalizing_scores_before_fusion](02_intermediate/10_normalizing_scores_before_fusion/) | Min-max vs. z-score, when a weighted blend is still worth it |
| 11 | [tuning_rrf_k](02_intermediate/11_tuning_rrf_k/) | RRF's `k` constant, and the tune/eval trap of sweeping it honestly |
| 12 | [metadata_aware_hybrid_retrieval](02_intermediate/12_metadata_aware_hybrid_retrieval/) | Source/category filters applied identically to both retrievers |
| 13 | [persisting_both_indexes](02_intermediate/13_persisting_both_indexes/) | Saving the dense and sparse index together, not rebuilding every run |
| 14 | [where_sparse_wins](02_intermediate/14_where_sparse_wins/) | A heuristic for spotting an ID-shaped, sparse-favoring query |
| 15 | [where_dense_wins](02_intermediate/15_where_dense_wins/) | Measuring literal vocabulary overlap to predict when dense is needed |
| 16 | [failure_modes_of_hybrid_retrieval](02_intermediate/16_failure_modes_of_hybrid_retrieval/) | A question where fusion still fails, on purpose, and why |
| 17 | [minimal_evaluation_dense_vs_sparse_vs_hybrid](02_intermediate/17_minimal_evaluation_dense_vs_sparse_vs_hybrid/) | precision@1, all three modes, side by side |
| 18 | [intermediate_checkpoint_project](02_intermediate/18_intermediate_checkpoint_project/) | **Checkpoint:** Persisted, Filterable Hybrid Assistant |

## Advanced: graduating both retrievers, and a capstone

| # | Lesson | Concept |
|---|--------|---------|
| 19 | [where_hand_rolled_retrieval_breaks_down](03_advanced/19_where_hand_rolled_retrieval_breaks_down/) | Timing hand-rolled dense and sparse as the corpus grows |
| 20 | [introducing_rank_bm25](03_advanced/20_introducing_rank_bm25/) | `BM25Okapi`, a real, precomputed BM25 implementation |
| 21 | [repointing_at_chromadb_and_rank_bm25](03_advanced/21_repointing_at_chromadb_and_rank_bm25/) | Both retrievers, real libraries, fused with the same RRF |
| 22 | [alpha_blended_fusion](03_advanced/22_alpha_blended_fusion/) | Alpha-blending revisited, head to head against RRF |
| 23 | [refactoring_into_ingest_and_ask](03_advanced/23_refactoring_into_ingest_and_ask/) | Two functions, the series' shared `Strategy` shape |
| 24 | [wrapping_it_as_a_service](03_advanced/24_wrapping_it_as_a_service/) | A minimal FastAPI endpoint around `ask()` |
| 25 | [advanced_capstone_project](03_advanced/25_advanced_capstone_project/) | **Capstone:** A Complete Hybrid RAG Service |
| 26 | [where_hybrid_rag_hits_a_wall](03_advanced/26_where_hybrid_rag_hits_a_wall/) | The failure modes that motivate the next courses in this series |
