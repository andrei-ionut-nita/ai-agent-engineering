# Course index

A linear, one-concept-per-lesson path through Agentic RAG: retrieval as
a tool the model chooses to call, not a hardcoded pipeline step. Built
from scratch, no LangChain or LlamaIndex, using Gemini's own native
function calling (`google-genai`) directly. Do these in order, top to
bottom, each lesson folder has a `README.md` (read first) and a
`lesson.py` (run second). Don't move to the next lesson until the
current one's checkpoint questions feel solid.

This is course 5 in a series organized by RAG architecture (mirroring
[andreinita.co/learning/rag-fundamentals](https://andreinita.co/learning/rag-fundamentals/)'s
map of nine architectures), building on
[naive_rag](../naive_rag/README.md), [hybrid_rag](../hybrid_rag/README.md),
[graph_rag](../graph_rag/README.md), and
[corrective_rag](../corrective_rag/README.md). Every prior course in
this series hardcodes retrieval as a fixed pipeline step; this course's
premise is that retrieval should be a *choice* the model makes, like
any other tool. It intentionally overlaps as little as possible with
`lessons/langchain`'s own agent lessons, which already teach agents
generically through a framework, this course is framework-free and
specifically about retrieval-as-a-tool: when an agent should retrieve,
how many times, and what else it should be able to call instead.

Setup: `GOOGLE_API_KEY` in a `.env` file at the project root (get a free
key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)),
no Docker, no database, no extra account. Then
`uv run python lessons/agentic_rag/<NN>_<name>/lesson.py` from the
project root.

## Beginner: retrieval as a tool the model can call

| # | Lesson | Concept |
|---|--------|---------|
| 01 | [what_is_agentic_rag](01_beginner/01_what_is_agentic_rag/) | Retrieval as a tool the model chooses to call, not a hardcoded pipeline step |
| 02 | [the_fixed_pipeline_assumption](01_beginner/02_the_fixed_pipeline_assumption/) | The always-retrieve pipeline every prior course used, made concrete |
| 03 | [gemini_function_calling_basics](01_beginner/03_gemini_function_calling_basics/) | `types.Tool`, `FunctionDeclaration`, `response.function_calls` |
| 04 | [retrieval_as_a_tool](01_beginner/04_retrieval_as_a_tool/) | Wrapping `search_notes()` as a callable Gemini tool |
| 05 | [a_single_step_agent_loop](01_beginner/05_a_single_step_agent_loop/) | Model call, tool call, tool result, final answer |
| 06 | [deciding_not_to_retrieve](01_beginner/06_deciding_not_to_retrieve/) | The same loop correctly skipping a tool it doesn't need |
| 07 | [multi_tool_agents](01_beginner/07_multi_tool_agents/) | A second, non-retrieval tool (`get_current_datetime`) |
| 08 | [end_to_end_agent_qa](01_beginner/08_end_to_end_agent_qa/) | One script, three question shapes, correct routing every time |
| 09 | [beginner_checkpoint_project](01_beginner/09_beginner_checkpoint_project/) | **Checkpoint:** A CLI Assistant That Decides |

## Intermediate: multi-step reasoning and bounded loops

| # | Lesson | Concept |
|---|--------|---------|
| 10 | [multi_step_loops](02_intermediate/10_multi_step_loops/) | A loop that keeps calling tools until the model stops asking |
| 11 | [query_planning_and_decomposition](02_intermediate/11_query_planning_and_decomposition/) | Steering the model to decompose a compound question |
| 12 | [passing_tool_results_back_correctly](02_intermediate/12_passing_tool_results_back_correctly/) | Why a tool result must follow its own function-call turn |
| 13 | [persisting_conversation_history](02_intermediate/13_persisting_conversation_history/) | Saving and reloading a structured, multi-turn transcript |
| 14 | [bounding_iterations](02_intermediate/14_bounding_iterations/) | `MAX_STEPS`, a guard that makes the loop provably terminate |
| 15 | [prompting_for_cited_multi_call_answers](02_intermediate/15_prompting_for_cited_multi_call_answers/) | Citing sources correctly across more than one tool call |
| 16 | [failure_modes_of_agentic_retrieval](02_intermediate/16_failure_modes_of_agentic_retrieval/) | Malformed calls, unnecessary retrieval, non-convergence, each deliberately triggered |
| 17 | [minimal_evaluation_retrieve_or_not](02_intermediate/17_minimal_evaluation_retrieve_or_not/) | Scoring the retrieve-or-not decision against a labeled set |
| 18 | [intermediate_checkpoint_project](02_intermediate/18_intermediate_checkpoint_project/) | **Checkpoint:** A Multi-Turn Notes Assistant |

## Advanced: a clean agent loop, and a capstone

| # | Lesson | Concept |
|---|--------|---------|
| 19 | [where_if_elif_dispatch_breaks_down](03_advanced/19_where_if_elif_dispatch_breaks_down/) | A third tool, declared but not dispatched, crashes on cue |
| 20 | [structuring_run_agent](03_advanced/20_structuring_run_agent/) | Separating loop mechanics from tool-specific dispatch |
| 21 | [a_tool_registry_pattern](03_advanced/21_a_tool_registry_pattern/) | `dict[str, Tool]` replacing if/elif, a third tool added cleanly |
| 22 | [optional_corrective_grading_as_a_tool](03_advanced/22_optional_corrective_grading_as_a_tool/) | Optional: wiring Corrective RAG's grading in as a fourth tool |
| 23 | [refactoring_into_tools_and_run_agent](03_advanced/23_refactoring_into_tools_and_run_agent/) | `tools()` + `run_agent()`, and this series' `ingest()`/`ask()` boundary |
| 24 | [wrapping_it_as_a_service](03_advanced/24_wrapping_it_as_a_service/) | A minimal FastAPI endpoint around `ask()` |
| 25 | [advanced_capstone_project](03_advanced/25_advanced_capstone_project/) | **Capstone:** A Complete Agentic RAG Service |
| 26 | [where_agentic_rag_hits_a_wall](03_advanced/26_where_agentic_rag_hits_a_wall/) | The failure modes that motivate Multimodal RAG |
