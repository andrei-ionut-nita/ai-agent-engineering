# Course index

A linear, one-concept-per-lesson path through Graph RAG, the
knowledge-graph-based retrieval architecture, built from scratch: no
LangChain, no LlamaIndex, just direct calls to Google's Gemini API
(`google-genai`), a hand-rolled adjacency-dict graph before graduating to
`networkx`, and `chromadb` for the vector half of the Advanced tier's
hybrid retrieval. Do these in order, top to bottom, each lesson folder
has a `README.md` (read first) and a `lesson.py` (run second). Don't
move to the next lesson until the current one's checkpoint questions
feel solid.

This is course 3 in a series organized by RAG architecture (mirroring
[andreinita.co/learning/rag-fundamentals](https://andreinita.co/learning/rag-fundamentals/)'s
map of nine architectures), following `lessons/naive_rag/` and
`lessons/hybrid_rag/`. It's distinct from `lessons/pggraph/`, which
teaches the Postgres AGE extension and Cypher, a different tool
entirely, not the Graph RAG *architecture* this course teaches:
extracting entities and relationships into a knowledge graph, then
answering multi-hop questions by traversing it.

Setup: `GOOGLE_API_KEY` in a `.env` file at the project root (get a free
key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)),
no Docker, no database, no extra account. Then
`uv run python lessons/graph_rag/<NN>_<name>/lesson.py` from the project
root.

## Beginner: extracting and traversing a graph by hand

| # | Lesson | Concept |
|---|--------|---------|
| 01 | [what_is_graph_rag](01_beginner/01_what_is_graph_rag/) | Multi-hop questions that chunk retrieval can't answer |
| 02 | [where_naive_retrieval_fails_multi_hop](01_beginner/02_where_naive_retrieval_fails_multi_hop/) | Watching Naive RAG's retrieval fail, live, on this course's fixtures |
| 03 | [extracting_entities_by_hand](01_beginner/03_extracting_entities_by_hand/) | Prompting Gemini for a list of named entities per document |
| 04 | [extracting_relationships_by_hand](01_beginner/04_extracting_relationships_by_hand/) | Prompting for `(subject, relation, object)` triples |
| 05 | [building_a_graph_by_hand](01_beginner/05_building_a_graph_by_hand/) | A graph as a plain Python adjacency dict |
| 06 | [graph_traversal_by_hand](01_beginner/06_graph_traversal_by_hand/) | One-hop and two-hop neighbor lookup |
| 07 | [answering_a_multi_hop_question](01_beginner/07_answering_a_multi_hop_question/) | Traverse to gather facts, then generate |
| 08 | [end_to_end_graph_qa](01_beginner/08_end_to_end_graph_qa/) | Extraction and traversal over every fixture note, one script |
| 09 | [beginner_checkpoint_project](01_beginner/09_beginner_checkpoint_project/) | **Checkpoint:** Graph Q&A CLI |

## Intermediate: making the graph practical

| # | Lesson | Concept |
|---|--------|---------|
| 10 | [combining_graph_and_vector_retrieval](02_intermediate/10_combining_graph_and_vector_retrieval/) | Embedding similarity to find a traversal's starting entity |
| 11 | [normalizing_ambiguous_entities](02_intermediate/11_normalizing_ambiguous_entities/) | Merging graph nodes that refer to the same real-world thing |
| 12 | [multi_document_graphs](02_intermediate/12_multi_document_graphs/) | Merging extraction across documents, with provenance tracking |
| 13 | [persisting_the_graph](02_intermediate/13_persisting_the_graph/) | Saving the graph to JSON instead of re-extracting every run |
| 14 | [limiting_traversal_depth](02_intermediate/14_limiting_traversal_depth/) | Why unbounded hops pull in exponentially more irrelevant context |
| 15 | [prompting_for_cited_multi_hop_answers](02_intermediate/15_prompting_for_cited_multi_hop_answers/) | Citing which source document each hop's fact came from |
| 16 | [failure_modes_of_graph_retrieval](02_intermediate/16_failure_modes_of_graph_retrieval/) | **Centerpiece:** error compounding across hops, shown live |
| 17 | [minimal_evaluation_chunk_vs_graph](02_intermediate/17_minimal_evaluation_chunk_vs_graph/) | Precision@k, chunk-based retrieval vs. graph-based retrieval |
| 18 | [intermediate_checkpoint_project](02_intermediate/18_intermediate_checkpoint_project/) | **Checkpoint:** Graph Q&A With Citations |

## Advanced: graduating the graph, and a capstone

| # | Lesson | Concept |
|---|--------|---------|
| 19 | [where_hand_rolled_graphs_break_down](03_advanced/19_where_hand_rolled_graphs_break_down/) | Timing the dict-based graph's `O(n²)` normalization cost |
| 20 | [introducing_networkx](03_advanced/20_introducing_networkx/) | `networkx.DiGraph`, shortest paths, reachability at any depth |
| 21 | [repointing_traversal_at_networkx](03_advanced/21_repointing_traversal_at_networkx/) | Same `build_graph`/`gather_facts` shape, a different backend |
| 22 | [graph_and_chromadb_hybrid_retrieval](03_advanced/22_graph_and_chromadb_hybrid_retrieval/) | `chromadb` for starting-node lookup, `networkx` for traversal |
| 23 | [refactoring_into_ingest_and_ask](03_advanced/23_refactoring_into_ingest_and_ask/) | Two functions: `ingest()`, `ask()`, this series' shared `Strategy` protocol |
| 24 | [wrapping_it_as_a_service](03_advanced/24_wrapping_it_as_a_service/) | A minimal FastAPI endpoint around `ask()` |
| 25 | [advanced_capstone_project](03_advanced/25_advanced_capstone_project/) | **Capstone:** A Complete Graph RAG Service |
| 26 | [where_graph_rag_hits_a_wall](03_advanced/26_where_graph_rag_hits_a_wall/) | The failure modes that motivate Corrective RAG, next in this series |
