# Course index

A linear, one-concept-per-lesson path through **LlamaIndex**, the
other major open-source RAG/agent framework in Python besides
LangChain. Do these in order, top to bottom, each lesson folder has a
`README.md` (read first) and a `lesson.py` (run second). Don't move to
the next lesson until the current one's checkpoint questions feel
solid.

Where LangChain (this repo's [langchain](../langchain/) course) is
**chain-centric**, its core abstraction a composable `Runnable` you
wire into arbitrary pipelines, LlamaIndex is **data-centric**: its
core abstraction is an `Index`, and the framework's whole shape is
built around one path, ingest documents, build an index, query it.
RAG isn't a feature you opt into here, it's the default thing the
framework does. Agents and tool-calling exist too (Lessons 14-17), but
as a layer on top of that indexing core, not the other way around.

This course assumes you've done [langchain](../langchain/) at least
through its RAG lessons (27-29), so it moves faster through ideas
you've already seen (embeddings, chunking, similarity search) and
spends its explanations on what's actually new: LlamaIndex's own
vocabulary, `Document`, `Node`, `Index`. Lesson 23 comes back the
other way, wrapping a LlamaIndex query engine as a tool inside a
LangGraph or Pydantic AI agent, so the two courses' agents can use
each other's strengths in the same system.

Setup: no new API key or service is required. LlamaIndex reuses the
same `GOOGLE_API_KEY` from `.env` and the same `uv sync`-installed
`.venv` as every other course in this repo, `llama-index`,
`llama-index-llms-google-genai`, and `llama-index-embeddings-google-genai`
are already in `pyproject.toml`. From the project root:

```bash
uv run python lessons/llamaindex/<tier>/<NN>_<name>/lesson.py
```

## Beginner: the core loop, Document to Node to Index to QueryEngine

| # | Lesson | Concept |
|---|--------|---------|
| 01 | [what_is_llamaindex](01_beginner/01_what_is_llamaindex/) | Data-centric vs LangChain's chain-centric design, when to reach for which |
| 02 | [documents_and_nodes](01_beginner/02_documents_and_nodes/) | `Document`, `SimpleDirectoryReader`, chunking into `Node`s |
| 03 | [connecting_gemini](01_beginner/03_connecting_gemini/) | The global `Settings.llm` / `Settings.embed_model` pattern |
| 04 | [first_vector_index](01_beginner/04_first_vector_index/) | `VectorStoreIndex.from_documents()`, embedding every Node |
| 05 | [querying_the_index](01_beginner/05_querying_the_index/) | `as_query_engine()`, `.query()`, the `Response` object |
| 06 | [retrievers](01_beginner/06_retrievers/) | `as_retriever()`, `similarity_top_k`, retrieval without synthesis |
| 07 | [response_modes](01_beginner/07_response_modes/) | `refine` vs `compact` vs `tree_summarize` synthesis |
| 08 | [chat_engines](01_beginner/08_chat_engines/) | `as_chat_engine()`, conversation memory across turns |
| 09 | [beginner_checkpoint_project](01_beginner/09_beginner_checkpoint_project/) | **Checkpoint:** a cited, grounded Q&A tool over the course's fixture docs |

## Intermediate: structure, tools, and agents

| # | Lesson | Concept |
|---|--------|---------|
| 10 | [structured_output](02_intermediate/10_structured_output/) | Pydantic-schema-constrained answers, `output_cls` |
| 11 | [metadata_and_filtering](02_intermediate/11_metadata_and_filtering/) | `MetadataFilters`, narrowing retrieval before it runs |
| 12 | [node_parsers_and_chunking_strategies](02_intermediate/12_node_parsers_and_chunking_strategies/) | `SentenceSplitter`, `TokenTextSplitter`, chunk size/overlap tradeoffs |
| 13 | [multi_document_indexes](02_intermediate/13_multi_document_indexes/) | Indexing distinct sources, per-document vs cross-document retrieval |
| 14 | [tools_and_function_calling](02_intermediate/14_tools_and_function_calling/) | `FunctionTool`, `predict_and_call()` |
| 15 | [agents_with_llamaindex](02_intermediate/15_agents_with_llamaindex/) | `FunctionAgent`, multi-step tool-calling decisions |
| 16 | [sub_question_query_engine](02_intermediate/16_sub_question_query_engine/) | Decomposing one question into sub-questions across multiple indexes |
| 17 | [intermediate_checkpoint_project](02_intermediate/17_intermediate_checkpoint_project/) | **Checkpoint:** an agent with both a RAG tool and a plain function tool |

## Advanced: evaluation, workflows, and production concerns

| # | Lesson | Concept |
|---|--------|---------|
| 18 | [evaluating_retrieval](03_advanced/18_evaluating_retrieval/) | `FaithfulnessEvaluator`, `RelevancyEvaluator` |
| 19 | [workflows](03_advanced/19_workflows/) | Event-driven pipelines via `llama_index.core.workflow` |
| 20 | [hybrid_search_and_reranking](03_advanced/20_hybrid_search_and_reranking/) | `LLMRerank` and other node postprocessors |
| 21 | [persisting_and_loading_indexes](03_advanced/21_persisting_and_loading_indexes/) | `StorageContext.persist()` / `load_index_from_storage()`, avoiding re-embedding |
| 22 | [observability_with_callbacks](03_advanced/22_observability_with_callbacks/) | `TokenCountingHandler`, `LlamaDebugHandler`, tracing what an index actually did |
| 23 | [swapping_into_langgraph_and_pydantic_ai](03_advanced/23_swapping_into_langgraph_and_pydantic_ai/) | A LlamaIndex query engine wrapped as a tool inside a LangGraph agent |
| 24 | [advanced_capstone_project](03_advanced/24_advanced_capstone_project/) | **Capstone:** multi-document agentic RAG with structured, validated output |
