# Course index

A linear, one-concept-per-lesson path through Multimodal RAG,
retrieval-augmented generation extended to cover images as well as
text. Course 6 in the RAG-architecture series (mirroring
[andreinita.co/learning/rag-fundamentals](https://andreinita.co/learning/rag-fundamentals/)'s
map of nine architectures), built on top of `naive_rag`'s exact
pipeline shape (chunk/caption, embed, retrieve, generate): the text
half is unchanged from `naive_rag`; the one new idea is
**captioning-then-embed**, describing an image in text with Gemini's
native image-input support, then embedding that caption with the same
`google-genai` text-embedding pipeline every course in this series
already uses. Do these in order, top to bottom, each lesson folder has
a `README.md` (read first) and a `lesson.py` (run second). Don't move
to the next lesson until the current one's checkpoint questions feel
solid.

Lesson 1 is explicit about a common misconception worth reading before
anything else: captioning-then-embed is *one* way to do multimodal
retrieval, not the only one. Joint embedding spaces (CLIP-style models
that embed images and text into one shared vector space directly, no
captioning step) are a different, equally legitimate approach this
course names but doesn't build, because captioning reuses the exact
pipeline every other course here already established and produces
plain, inspectable text instead of an opaque vector.

Setup: `GOOGLE_API_KEY` in a `.env` file at the project root (get a free
key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)),
no Docker, no database, no extra account. Then
`uv run python lessons/multimodal_rag/<NN>_<name>/lesson.py` from the
project root.

## Beginner: captioning images into a retrievable form

| # | Lesson | Concept |
|---|--------|---------|
| 01 | [what_is_multimodal_rag](01_beginner/01_what_is_multimodal_rag/) | Captioning-then-embed vs. joint embedding spaces, and why this course picks captioning |
| 02 | [the_blind_spot_of_text_only_retrieval](01_beginner/02_the_blind_spot_of_text_only_retrieval/) | Text-only RAG retrieves the right document, still can't answer |
| 03 | [sending_an_image_to_gemini](01_beginner/03_sending_an_image_to_gemini/) | `types.Part.from_bytes`, your first multimodal `generate_content` call |
| 04 | [captioning_an_image](01_beginner/04_captioning_an_image/) | Prompting for retrievable, specific detail |
| 05 | [embedding_image_captions](01_beginner/05_embedding_image_captions/) | The same embedding pipeline, applied to caption text |
| 06 | [a_mixed_vector_store](01_beginner/06_a_mixed_vector_store/) | Text chunks and image captions, one list |
| 07 | [retrieval_across_modalities](01_beginner/07_retrieval_across_modalities/) | The unmodified `retrieve()`, now finding an image's caption |
| 08 | [generation_with_the_original_image](01_beginner/08_generation_with_the_original_image/) | Re-attaching the real image (not just its caption) at generation time |
| 09 | [beginner_checkpoint_project](01_beginner/09_beginner_checkpoint_project/) | **Checkpoint:** CLI Q&A Over Notes and Images |

## Intermediate: multiple images, metadata, and evaluation

| # | Lesson | Concept |
|---|--------|---------|
| 10 | [captioning_multiple_images_per_document](02_intermediate/10_captioning_multiple_images_per_document/) | Figure order, `parent_document`/`figure_number` |
| 11 | [modality_metadata](02_intermediate/11_modality_metadata/) | An explicit `modality` field, not an implicit `image_path is not None` |
| 12 | [persisting_captions_and_embeddings](02_intermediate/12_persisting_captions_and_embeddings/) | Saving the mixed store so images aren't re-captioned every run |
| 13 | [balancing_k_across_modalities](02_intermediate/13_balancing_k_across_modalities/) | Ranking each modality separately, guaranteeing a mix |
| 14 | [prompting_for_modality_cited_answers](02_intermediate/14_prompting_for_modality_cited_answers/) | Citations naming both the file and the modality |
| 15 | [failure_modes_of_captioning_and_matching](02_intermediate/15_failure_modes_of_captioning_and_matching/) | A dropped detail, and a caption that matches without the image answering |
| 16 | [minimal_evaluation_text_vs_image_questions](02_intermediate/16_minimal_evaluation_text_vs_image_questions/) | precision@k, broken down by modality |
| 17 | [extracting_images_from_a_pdf](02_intermediate/17_extracting_images_from_a_pdf/) | `pypdf`'s `page.images`, before captioning |
| 18 | [intermediate_checkpoint_project](02_intermediate/18_intermediate_checkpoint_project/) | **Checkpoint:** Notes-and-Diagrams Search Assistant |

## Advanced: graduating the mixed store, and a capstone

| # | Lesson | Concept |
|---|--------|---------|
| 19 | [where_per_query_captioning_gets_expensive](03_advanced/19_where_per_query_captioning_gets_expensive/) | Timing captioning (once) vs. re-attachment (every retrieval) |
| 20 | [introducing_chromadb_for_the_mixed_store](03_advanced/20_introducing_chromadb_for_the_mixed_store/) | `chromadb`, both modalities in one collection |
| 21 | [metadata_filtering_by_modality](03_advanced/21_metadata_filtering_by_modality/) | `where={"modality": ...}`, text-only, image-only, or both |
| 22 | [refactoring_into_ingest_and_ask](03_advanced/22_refactoring_into_ingest_and_ask/) | `ingest()`/`ask()`, this course's `Strategy` protocol, `State` defined |
| 23 | [wrapping_it_as_a_service](03_advanced/23_wrapping_it_as_a_service/) | A minimal FastAPI wrapper, `naive_rag` Lesson 24's shape, unchanged |
| 24 | [serving_the_original_image_back](03_advanced/24_serving_the_original_image_back/) | Returning the actual image to the caller, not just describing it |
| 25 | [advanced_capstone_project](03_advanced/25_advanced_capstone_project/) | **Capstone:** A Complete Multimodal RAG Service |
| 26 | [where_multimodal_rag_hits_a_wall](03_advanced/26_where_multimodal_rag_hits_a_wall/) | The failure modes that motivate the next course in this series |
