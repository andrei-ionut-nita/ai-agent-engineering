# Course index

A linear, one-concept-per-lesson path through Pydantic AI: a type-safe
agent framework from the Pydantic team. Where `langchain` builds agents
around string prompts and `bind_tools`, Pydantic AI builds them around
validated Python types: your agent's output is a Pydantic model, not a
string you hope is JSON. Do these in order, top to bottom, each lesson
folder has a `README.md` (read first) and a `lesson.py` (run second).
Don't move to the next lesson until the current one's checkpoint
questions feel solid.

This course assumes you've done the [langchain](../langchain/) course.
Every lesson calls out the LangChain equivalent of the concept it's
introducing, since the ideas (tools, dependency injection, multi-agent
delegation, tracing, MCP) are the same ones, just with a different,
more type-strict shape. Lesson 17 also assumes [langgraph](../langgraph/)
Lessons 1-6, lesson 18 assumes [langsmith](../langsmith/) Lessons 1-4,
and Lesson 21 assumes the [mcp](../mcp/) course through Lesson 12.

Setup: `GOOGLE_API_KEY` in a `.env` file at the project root (get a
free key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)),
then `uv run python lessons/pydantic_ai/<NN>_<name>/lesson.py` from the
project root. Every lesson uses the model string `"google:gemini-3.5-flash-lite"`,
Pydantic AI's equivalent of `ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")`
in the other courses.

## Beginner: the core Agent API, one concept at a time

| # | Lesson | Concept |
|---|--------|---------|
| 01 | [what_is_pydantic_ai](01_beginner/01_what_is_pydantic_ai/) | The pitch: validated types in and out, vs. a string in, a string out |
| 02 | [first_agent](01_beginner/02_first_agent/) | `Agent(...)`, `run_sync`, reading `result.output` |
| 03 | [structured_output_with_output_type](01_beginner/03_structured_output_with_output_type/) | A `BaseModel` as `output_type`, guaranteed-valid output |
| 04 | [system_prompts](01_beginner/04_system_prompts/) | Static `system_prompt=` and dynamic `@agent.system_prompt` |
| 05 | [dependency_injection](01_beginner/05_dependency_injection/) | `deps_type`, `RunContext`, passing runtime state into a run |
| 06 | [tools_basics](01_beginner/06_tools_basics/) | `@agent.tool_plain`, function tools the model can call |
| 07 | [tool_with_deps](01_beginner/07_tool_with_deps/) | `@agent.tool`, tools that read `RunContext.deps` |
| 08 | [output_validators_and_retries](01_beginner/08_output_validators_and_retries/) | `@agent.output_validator`, raising `ModelRetry` |
| 09 | [streaming_output](01_beginner/09_streaming_output/) | `run_stream`, structured output as it's still being generated |
| 10 | [beginner_checkpoint_project](01_beginner/10_beginner_checkpoint_project/) | **Checkpoint:** a validated research-notes assistant |

## Intermediate: composing, testing, and evaluating agents

| # | Lesson | Concept |
|---|--------|---------|
| 11 | [multi_turn_conversations](02_intermediate/11_multi_turn_conversations/) | `message_history`, `result.all_messages()`, continuing a chat |
| 12 | [multi_agent_delegation](02_intermediate/12_multi_agent_delegation/) | One agent calling another agent as a tool |
| 13 | [usage_limits_and_cost_tracking](02_intermediate/13_usage_limits_and_cost_tracking/) | `UsageLimits`, reading `result.usage` |
| 14 | [testing_agents_with_testmodel](02_intermediate/14_testing_agents_with_testmodel/) | `TestModel`, unit-testing agent logic with no real API calls |
| 15 | [pydantic_evals_basics](02_intermediate/15_pydantic_evals_basics/) | `pydantic_evals`: `Case`, `Dataset`, evaluators (the `langsmith` equivalent) |
| 16 | [structured_output_unions](02_intermediate/16_structured_output_unions/) | A `Union` output type, the agent picking its own response shape |
| 17 | [graph_based_agents_with_pydantic_graph](02_intermediate/17_graph_based_agents_with_pydantic_graph/) | `pydantic_graph`: explicit steps and edges (the `langgraph` equivalent) |
| 18 | [observability_with_logfire](02_intermediate/18_observability_with_logfire/) | OpenTelemetry-based instrumentation (the `langsmith` tracing equivalent) |
| 19 | [intermediate_checkpoint_project](02_intermediate/19_intermediate_checkpoint_project/) | **Checkpoint:** a multi-agent support triage system with an eval dataset |

## Advanced: production concerns and interop

| # | Lesson | Concept |
|---|--------|---------|
| 20 | [human_in_the_loop_deferred_tools](03_advanced/20_human_in_the_loop_deferred_tools/) | `requires_approval=True`, resuming a run after a human decides |
| 21 | [pydantic_ai_as_mcp_client](03_advanced/21_pydantic_ai_as_mcp_client/) | `MCPToolset` + `StdioTransport`, using an MCP server's tools directly |
| 22 | [model_fallback_and_provider_config](03_advanced/22_model_fallback_and_provider_config/) | `FallbackModel`, swapping models/providers without touching agent code |
| 23 | [durable_execution_patterns](03_advanced/23_durable_execution_patterns/) | Retries, timeouts, and idempotency for agents running in production |
| 24 | [advanced_capstone_project](03_advanced/24_advanced_capstone_project/) | **Capstone:** validated I/O, tools, an MCP-connected tool, evals, and a fallback model |
