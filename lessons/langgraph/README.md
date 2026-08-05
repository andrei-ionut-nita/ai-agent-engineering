# Course index

A linear, one-concept-per-lesson path through LangGraph, the graph
engine LangChain's own agents are built on, using Google's Gemini free
tier (`gemini-3.5-flash-lite`). This course assumes you've done the
[langchain](../langchain/) course first, or already know `.invoke()`,
messages, and `@tool`, it does not re-teach those. Do these lessons in
order, top to bottom, each lesson folder has a `README.md` (read first)
and a `lesson.py` (run second). Don't move to the next lesson until the
current one's checkpoint questions feel solid.

Setup: `GOOGLE_API_KEY` in a `.env` file at the project root (get a free
key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)),
then `uv run python lessons/langgraph/<NN>_<name>/lesson.py` from the
project root.

## Beginner: the graph primitives, no memory or tools yet

| # | Lesson | Concept |
|---|--------|---------|
| 01 | [first_graph](01_beginner/01_first_graph/) | `StateGraph`, nodes, `add_edge`, `START`/`END` |
| 02 | [state_and_reducers](01_beginner/02_state_and_reducers/) | `Annotated` fields, reducers, merged vs. replaced state |
| 03 | [multiple_nodes_linear](01_beginner/03_multiple_nodes_linear/) | Chaining several nodes into a pipeline |
| 04 | [conditional_edges](01_beginner/04_conditional_edges/) | `add_conditional_edges`, routing on state |
| 05 | [cycles_and_loops](01_beginner/05_cycles_and_loops/) | A node routing back to itself until a condition holds |
| 06 | [messages_state](01_beginner/06_messages_state/) | `MessagesState`, `add_messages`, calling a model inside a node |
| 07 | [tool_node](01_beginner/07_tool_node/) | `ToolNode`, `tools_condition`, a graph that can act |
| 08 | [streaming_values_updates](01_beginner/08_streaming_values_updates/) | `.stream()`, `stream_mode="values"` vs `"updates"` |
| 09 | [streaming_tokens](01_beginner/09_streaming_tokens/) | `stream_mode="messages"`, token-by-token output |
| 10 | [invoke_config_and_recursion](01_beginner/10_invoke_config_and_recursion/) | The `config` dict, `recursion_limit` |
| 11 | [visualizing_the_graph](01_beginner/11_visualizing_the_graph/) | `get_graph()`, seeing the shape of what you built |
| 12 | [beginner_checkpoint_project](01_beginner/12_beginner_checkpoint_project/) | **Checkpoint:** Text-Processing Pipeline Graph |

## Intermediate: memory, persistence, parallelism, control flow

| # | Lesson | Concept |
|---|--------|---------|
| 13 | [checkpointer_memory](02_intermediate/13_checkpointer_memory/) | `InMemorySaver`, `thread_id`, memory between calls |
| 14 | [persistent_checkpointer](02_intermediate/14_persistent_checkpointer/) | `SqliteSaver`, memory across restarts |
| 15 | [human_in_the_loop_interrupt](02_intermediate/15_human_in_the_loop_interrupt/) | `interrupt()`, pausing for a human, resuming |
| 16 | [time_travel_state_history](02_intermediate/16_time_travel_state_history/) | `get_state_history`, rewinding and forking |
| 17 | [parallel_fan_out_fan_in](02_intermediate/17_parallel_fan_out_fan_in/) | Several nodes running at once, then merging |
| 18 | [send_api_map_reduce](02_intermediate/18_send_api_map_reduce/) | `Send`, fanning out dynamically over a list |
| 19 | [subgraphs](02_intermediate/19_subgraphs/) | A whole graph used as a single node |
| 20 | [command_objects](02_intermediate/20_command_objects/) | `Command`, updating state and routing in one step |
| 21 | [retry_and_error_handling](02_intermediate/21_retry_and_error_handling/) | `RetryPolicy`, a node that fails gracefully |
| 22 | [intermediate_checkpoint_project](02_intermediate/22_intermediate_checkpoint_project/) | **Checkpoint:** Persistent Approval Workflow |

## Advanced: agents, multi-agent systems, production concerns

| # | Lesson | Concept |
|---|--------|---------|
| 23 | [building_an_agent_from_scratch](03_advanced/23_building_an_agent_from_scratch/) | The ReAct loop, built from raw nodes and edges |
| 24 | [structured_output_in_a_graph](03_advanced/24_structured_output_in_a_graph/) | `with_structured_output` inside a node |
| 25 | [long_term_memory_store](03_advanced/25_long_term_memory_store/) | `InMemoryStore`, memory that outlives a thread |
| 26 | [multi_agent_handoffs](03_advanced/26_multi_agent_handoffs/) | `Command(goto=...)`, one agent handing off to a peer |
| 27 | [multi_agent_supervisor_graph](03_advanced/27_multi_agent_supervisor_graph/) | A supervisor node routing to specialist subgraphs |
| 28 | [context_trimming_in_a_node](03_advanced/28_context_trimming_in_a_node/) | Trimming messages before they reach the model |
| 29 | [rag_node](03_advanced/29_rag_node/) | A retrieval node feeding a generation node |
| 30 | [dynamic_breakpoints](03_advanced/30_dynamic_breakpoints/) | `interrupt_before`/`interrupt_after`, conditional pausing |
| 31 | [middleware_style_guardrails](03_advanced/31_middleware_style_guardrails/) | Guardrail nodes wrapping the real work |
| 32 | [tracing_and_observability](03_advanced/32_tracing_and_observability/) | Watching a graph run step by step |
| 33 | [async_and_concurrency](03_advanced/33_async_and_concurrency/) | `ainvoke`/`astream`, running nodes concurrently |
| 34 | [deploying_persistent_agent](03_advanced/34_deploying_persistent_agent/) | Combining `SqliteSaver` and a store for a durable agent |
| 35 | [advanced_capstone_project](03_advanced/35_advanced_capstone_project/) | **Capstone:** Multi-Agent Research Assistant Graph |
