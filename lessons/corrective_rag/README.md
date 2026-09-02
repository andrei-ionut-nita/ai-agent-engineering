# Course index

A linear, one-concept-per-lesson path through Corrective RAG (CRAG):
grading retrieved chunks for relevance, filtering or refining what
generation actually sees, and correcting a bad retrieval before it ever
reaches the model, built from scratch before graduating to `chromadb`:
no LangChain, no LlamaIndex, direct calls to Google's Gemini API
(`google-genai`). Do these in order, top to bottom, each lesson folder
has a `README.md` (read first) and a `lesson.py` (run second). Don't
move to the next lesson until the current one's checkpoint questions
feel solid.

This is course 4 in a series organized by RAG architecture (mirroring
[andreinita.co/learning/rag-fundamentals](https://andreinita.co/learning/rag-fundamentals/)'s
map of nine architectures). It assumes you've done
[`lessons/naive_rag/`](../naive_rag/) (course 1) or otherwise already
know embeddings, cosine similarity, top-`k` retrieval, and why naive
retrieval can confidently return the wrong chunk, Lesson 2 here is a
compressed recap of that exact failure, not a full re-teach.

This course teaches the mechanism from Yan et al. 2024, "Corrective
Retrieval Augmented Generation" (arXiv:2401.15884): a retrieval
evaluator that grades each chunk's confidence, knowledge refinement on
the chunks graded "correct," and external web search as the fallback
for chunks graded "incorrect." Lesson 1 names two deliberate
simplifications this course makes along the way, and says exactly which
later lesson closes each gap.

Setup: `GOOGLE_API_KEY` in a `.env` file at the project root (get a free
key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)),
no Docker, no database, no extra account. Then
`uv run python lessons/corrective_rag/<NN>_<name>/lesson.py` from the
project root.

## Beginner: grading and correcting retrieval by hand

| # | Lesson | Concept |
|---|--------|---------|
| 01 | [what_is_corrective_rag](01_beginner/01_what_is_corrective_rag/) | Retrieval can silently return irrelevant chunks, generation never finds out |
| 02 | [where_naive_retrieval_is_confidently_wrong](01_beginner/02_where_naive_retrieval_is_confidently_wrong/) | Recap: a confidently-wrong top-k chunk, watched happening again |
| 03 | [grading_a_retrieved_chunk](01_beginner/03_grading_a_retrieved_chunk/) | Prompting Gemini for a binary relevant / not-relevant call |
| 04 | [grading_all_top_k_chunks](01_beginner/04_grading_all_top_k_chunks/) | Grading every retrieved chunk, not just the top one |
| 05 | [filtering_out_incorrect_chunks](01_beginner/05_filtering_out_incorrect_chunks/) | Dropping not-relevant chunks before they reach generation |
| 06 | [query_rewriting](01_beginner/06_query_rewriting/) | Rephrasing the query when every chunk grades not-relevant |
| 07 | [re_retrieval_with_the_rewritten_query](01_beginner/07_re_retrieval_with_the_rewritten_query/) | Re-running retrieval with the rewritten query |
| 08 | [end_to_end_corrective_qa](01_beginner/08_end_to_end_corrective_qa/) | Retrieve, grade, filter/rewrite, re-retrieve, generate, one script |
| 09 | [beginner_checkpoint_project](01_beginner/09_beginner_checkpoint_project/) | **Checkpoint:** CLI Q&A That Self-Corrects |

## Intermediate: making correction precise and bounded

| # | Lesson | Concept |
|---|--------|---------|
| 10 | [strip_level_grading](02_intermediate/10_strip_level_grading/) | Grading a chunk's individual sentences, not the whole chunk |
| 11 | [recomposing_context_from_relevant_strips](02_intermediate/11_recomposing_context_from_relevant_strips/) | Keeping only relevant strips instead of a whole chunk |
| 12 | [confidence_buckets_and_actions](02_intermediate/12_confidence_buckets_and_actions/) | Upgrading the binary grade to correct / ambiguous / incorrect |
| 13 | [persisting_grading_results](02_intermediate/13_persisting_grading_results/) | Saving grades alongside the vector store, not re-grading every run |
| 14 | [query_rewriting_strategies](02_intermediate/14_query_rewriting_strategies/) | Broadening, narrowing, and decomposing a rewritten query |
| 15 | [prompting_for_disclosed_corrections](02_intermediate/15_prompting_for_disclosed_corrections/) | Answers that say when and why a correction happened |
| 16 | [failure_modes_of_grading_and_rewriting](02_intermediate/16_failure_modes_of_grading_and_rewriting/) | Grader/generator circularity, shown, not just told about |
| 17 | [minimal_evaluation_before_vs_after_correction](02_intermediate/17_minimal_evaluation_before_vs_after_correction/) | precision@k and answer quality, before vs. after correction |
| 18 | [intermediate_checkpoint_project](02_intermediate/18_intermediate_checkpoint_project/) | **Checkpoint:** Notes Search with a "Corrected" Indicator |

## Advanced: making correction affordable, and a capstone

| # | Lesson | Concept |
|---|--------|---------|
| 19 | [where_per_chunk_grading_gets_expensive](03_advanced/19_where_per_chunk_grading_gets_expensive/) | Counting grading calls as the corpus and `k` grow |
| 20 | [a_cheap_pre_filter_before_grading](03_advanced/20_a_cheap_pre_filter_before_grading/) | A similarity-score floor before the LLM grader runs at all |
| 21 | [bounding_correction_loops](03_advanced/21_bounding_correction_loops/) | A max-rewrite-attempts guard before falling back to "I don't know" |
| 22 | [external_web_search_as_the_incorrect_branch](03_advanced/22_external_web_search_as_the_incorrect_branch/) | The paper's real "incorrect" branch, pluggable and stubbed |
| 23 | [refactoring_into_ingest_grade_correct_ask](03_advanced/23_refactoring_into_ingest_grade_correct_ask/) | The series' shared `Strategy` shape, `State = (collection, grader)` |
| 24 | [wrapping_it_as_a_service](03_advanced/24_wrapping_it_as_a_service/) | A minimal FastAPI endpoint around `ask()` |
| 25 | [advanced_capstone_project](03_advanced/25_advanced_capstone_project/) | **Capstone:** A Complete Corrective RAG Service |
| 26 | [where_corrective_rag_hits_a_wall](03_advanced/26_where_corrective_rag_hits_a_wall/) | The failure modes that motivate Agentic RAG |
