# Course index

A linear, one-concept-per-lesson path through Naive (Standard) RAG, the
baseline retrieval-augmented generation architecture, built from scratch:
no LangChain, no LlamaIndex, just direct calls to Google's Gemini API
(`google-genai`) and a plain Python list standing in for a vector
database. Do these in order, top to bottom, each lesson folder has a
`README.md` (read first) and a `lesson.py` (run second). Don't move to
the next lesson until the current one's checkpoint questions feel solid.

This is the first course in a series organized by RAG architecture
(mirroring [andreinita.co/learning/rag-fundamentals](https://andreinita.co/learning/rag-fundamentals/)'s
map of nine architectures), rather than by library like this repo's other
courses. It intentionally overlaps as little as possible with
`lessons/pgvector/`, `lessons/llamaindex/`, and `lessons/ollama/`'s own
RAG lessons: those teach RAG *through* a framework or database; this one
teaches what those frameworks are doing underneath, by writing it by
hand first.

Setup: `GOOGLE_API_KEY` in a `.env` file at the project root (get a free
key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)),
no Docker, no database, no extra account. Then
`uv run python lessons/naive_rag/<NN>_<name>/lesson.py` from the project
root.

## Beginner: hand-rolled RAG, one piece at a time

| # | Lesson | Concept |
|---|--------|---------|
| 01 | [what_is_naive_rag](01_beginner/01_what_is_naive_rag/) | The three-stage shape: chunk, embed, retrieve, generate |
| 02 | [your_first_embedding](01_beginner/02_your_first_embedding/) | `embed_content`, a vector as a list of floats |
| 03 | [cosine_similarity_by_hand](01_beginner/03_cosine_similarity_by_hand/) | Dot product, magnitude, "similar" as a number |
| 04 | [chunking_a_document](01_beginner/04_chunking_a_document/) | Splitting one document into retrievable passages |
| 05 | [an_in_memory_vector_store](01_beginner/05_an_in_memory_vector_store/) | A list of `{text, embedding}` dicts |
| 06 | [retrieval_top_k](01_beginner/06_retrieval_top_k/) | Ranking chunks by similarity, taking the top `k` |
| 07 | [generation_stuffing_the_prompt](01_beginner/07_generation_stuffing_the_prompt/) | Putting retrieved text into the prompt |
| 08 | [end_to_end_single_document_qa](01_beginner/08_end_to_end_single_document_qa/) | The full pipeline, one script, one document |
| 09 | [beginner_checkpoint_project](01_beginner/09_beginner_checkpoint_project/) | **Checkpoint:** CLI Q&A Over a Folder |

## Intermediate: where naive RAG breaks, and the fixes that keep it naive

| # | Lesson | Concept |
|---|--------|---------|
| 10 | [chunk_size_and_overlap](02_intermediate/10_chunk_size_and_overlap/) | Same document, bad vs. good chunking, side by side |
| 11 | [structure_aware_chunking](02_intermediate/11_structure_aware_chunking/) | Splitting on headings/paragraphs instead of a fixed size |
| 12 | [multiple_documents_and_metadata](02_intermediate/12_multiple_documents_and_metadata/) | Tagging each chunk with its source file |
| 13 | [persisting_the_vector_store](02_intermediate/13_persisting_the_vector_store/) | Saving embeddings to JSON instead of re-embedding every run |
| 14 | [choosing_k_and_thresholds](02_intermediate/14_choosing_k_and_thresholds/) | Dropping irrelevant top-`k` hits with a similarity floor |
| 15 | [prompting_for_grounded_answers](02_intermediate/15_prompting_for_grounded_answers/) | Citing sources, saying "I don't know" |
| 16 | [failure_modes_by_hand](02_intermediate/16_failure_modes_by_hand/) | A multi-hop question and a split-chunk answer, both fail visibly |
| 17 | [minimal_evaluation_precision_at_k](02_intermediate/17_minimal_evaluation_precision_at_k/) | A labeled Q&A set, scored by hand |
| 18 | [intermediate_checkpoint_project](02_intermediate/18_intermediate_checkpoint_project/) | **Checkpoint:** Notes Search Assistant with Citations |

## Advanced: graduating the hand-rolled store, and a capstone

| # | Lesson | Concept |
|---|--------|---------|
| 19 | [where_linear_scan_breaks_down](03_advanced/19_where_linear_scan_breaks_down/) | Timing the list-based search as the corpus grows |
| 20 | [introducing_chromadb](03_advanced/20_introducing_chromadb/) | `chromadb.Client()`, a real, still-local vector database |
| 21 | [repointing_retrieval_at_chromadb](03_advanced/21_repointing_retrieval_at_chromadb/) | Same `ingest`/`retrieve` shape, a different backend |
| 22 | [metadata_filtering_with_chromadb](03_advanced/22_metadata_filtering_with_chromadb/) | `where` filters, retrieval scoped to a source |
| 23 | [refactoring_into_ingest_and_ask](03_advanced/23_refactoring_into_ingest_and_ask/) | Two functions: `ingest()`, `ask()` |
| 24 | [wrapping_it_as_a_service](03_advanced/24_wrapping_it_as_a_service/) | A minimal FastAPI endpoint around `ask()` |
| 25 | [advanced_capstone_project](03_advanced/25_advanced_capstone_project/) | **Capstone:** A Complete Naive RAG Service |
| 26 | [where_naive_rag_hits_a_wall](03_advanced/26_where_naive_rag_hits_a_wall/) | The failure modes that motivate the next course in this series |
