# Course index

A linear, one-concept-per-lesson path through LangChain and agent
building, using Google's Gemini free tier (`gemini-3.5-flash-lite`). Do
these in order, top to bottom, each lesson folder has a `README.md`
(read first) and a `lesson.py` (run second). Don't move to the next
lesson until the current one's checkpoint questions feel solid.

Setup: `GOOGLE_API_KEY` in a `.env` file at the project root (get a free
key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)),
then `uv run python lessons/langchain/<NN>_<name>/lesson.py` from the project root.

## Beginner: core LangChain mechanics, no tools or agents yet

| # | Lesson | Concept |
|---|--------|---------|
| 01 | [first_call](01_beginner/01_first_call/) | `.invoke()`, API keys, the model object |
| 02 | [message_types](01_beginner/02_message_types/) | `SystemMessage`/`HumanMessage`/`AIMessage` |
| 03 | [prompt_templates](01_beginner/03_prompt_templates/) | `ChatPromptTemplate`, filling in a blank |
| 04 | [template_variables_and_partials](01_beginner/04_template_variables_and_partials/) | Multiple blanks, `.partial()` |
| 05 | [few_shot_prompting](01_beginner/05_few_shot_prompting/) | Teaching by example instead of instruction |
| 06 | [chains_lcel](01_beginner/06_chains_lcel/) | Composing steps with `\|` |
| 07 | [output_parsers](01_beginner/07_output_parsers/) | `StrOutputParser`, `JsonOutputParser` |
| 08 | [runnable_lambda](01_beginner/08_runnable_lambda/) | Wrapping your own function into a chain |
| 09 | [batching_and_async](01_beginner/09_batching_and_async/) | `.batch()`, `.ainvoke()`, concurrency |
| 10 | [model_parameters](01_beginner/10_model_parameters/) | `temperature`, `max_output_tokens` |
| 11 | [provider_agnostic_models](01_beginner/11_provider_agnostic_models/) | `init_chat_model` |
| 12 | [beginner_checkpoint_project](01_beginner/12_beginner_checkpoint_project/) | **Checkpoint:** Prompted Story Generator |

## Intermediate: giving the model abilities, real-world rough edges

| # | Lesson | Concept |
|---|--------|---------|
| 13 | [defining_tools](02_intermediate/13_defining_tools/) | `@tool`, what a tool actually is |
| 14 | [tool_calling](02_intermediate/14_tool_calling/) | `bind_tools`, the manual ask/run/ask loop |
| 15 | [multiple_tools](02_intermediate/15_multiple_tools/) | The model choosing between several tools |
| 16 | [tool_error_handling](02_intermediate/16_tool_error_handling/) | A failing tool call, without crashing |
| 17 | [conversation_memory](02_intermediate/17_conversation_memory/) | Memory = resending the whole history |
| 18 | [structured_output](02_intermediate/18_structured_output/) | `with_structured_output`, reliable data |
| 19 | [streaming](02_intermediate/19_streaming/) | `.stream()` vs waiting for the full reply |
| 20 | [multimodal_input](02_intermediate/20_multimodal_input/) | Sending an image alongside text |
| 21 | [retries_and_rate_limits](02_intermediate/21_retries_and_rate_limits/) | Handling transient `429`/`503` errors |
| 22 | [intermediate_checkpoint_project](02_intermediate/22_intermediate_checkpoint_project/) | **Checkpoint:** CLI Assistant with a Tool and Memory |

## Advanced: real agents, context management, production concerns

| # | Lesson | Concept |
|---|--------|---------|
| 23 | [create_agent_basics](03_advanced/23_create_agent_basics/) | `create_agent`, automating the tool loop |
| 24 | [agent_memory_checkpointer](03_advanced/24_agent_memory_checkpointer/) | `InMemorySaver`, `thread_id` |
| 25 | [context_trimming](03_advanced/25_context_trimming/) | `trim_messages`, dropping old messages |
| 26 | [conversation_summarization](03_advanced/26_conversation_summarization/) | Compressing old messages instead |
| 27 | [document_loading_and_splitting](03_advanced/27_document_loading_and_splitting/) | `Document`, text splitters |
| 28 | [rag_embeddings_and_vectorstore](03_advanced/28_rag_embeddings_and_vectorstore/) | Embeddings, searching by meaning |
| 29 | [rag_as_a_tool](03_advanced/29_rag_as_a_tool/) | Wrapping RAG search as an agent tool |
| 30 | [human_in_the_loop](03_advanced/30_human_in_the_loop/) | `interrupt_before`, pausing for approval |
| 31 | [multi_agent_supervisor](03_advanced/31_multi_agent_supervisor/) | An agent delegating to other agents |
| 32 | [persistent_checkpointer](03_advanced/32_persistent_checkpointer/) | `SqliteSaver`, memory across restarts |
| 33 | [agent_middleware_and_guardrails](03_advanced/33_agent_middleware_and_guardrails/) | `@before_model`, automatic guardrails |
| 34 | [tracing_and_observability](03_advanced/34_tracing_and_observability/) | Callback handlers, seeing what happened |
| 35 | [advanced_capstone_project](03_advanced/35_advanced_capstone_project/) | **Capstone:** Local Research Assistant Agent |
