# Course index

A linear, one-concept-per-lesson path through LangSmith, the tracing,
evaluation, and monitoring platform for LLM applications. This course
assumes you've done the [langchain](../langchain/) and
[langgraph](../langgraph/) courses first, it traces and evaluates the
agents built there instead of re-explaining LangChain/LangGraph basics.
Do these lessons in order, top to bottom, each lesson folder has a
`README.md` (read first) and a `lesson.py` (run second). Don't move to
the next lesson until the current one's checkpoint questions feel solid.

Setup: everything from the other two courses (`GOOGLE_API_KEY`), plus a
free LangSmith account. Sign up at
[smith.langchain.com](https://smith.langchain.com), create an API key,
and add to the `.env` file at the project root:

```
LANGSMITH_API_KEY=your-key-here
LANGSMITH_TRACING=true
```

Then `uv run python lessons/langsmith/<NN>_<name>/lesson.py` from the
project root, and check [smith.langchain.com](https://smith.langchain.com)
after each run to see what was recorded.

## Beginner: tracing, no evaluation yet

| # | Lesson | Concept |
|---|--------|---------|
| 01 | [setup_and_first_trace](01_beginner/01_setup_and_first_trace/) | `LANGSMITH_TRACING`, the `@traceable` decorator, your first trace |
| 02 | [tracing_basics](01_beginner/02_tracing_basics/) | Nested `@traceable` calls, the run tree in the UI |
| 03 | [types_of_runs](01_beginner/03_types_of_runs/) | `run_type` (`llm`/`chain`/`tool`/`retriever`), metadata, tags |
| 04 | [alternative_tracing_methods](01_beginner/04_alternative_tracing_methods/) | `trace()` context manager, wrapping a client, raw `RunTree` |
| 05 | [conversational_threads](01_beginner/05_conversational_threads/) | `thread_id`, grouping multi-turn runs in the UI |
| 06 | [tracing_a_langgraph_agent](01_beginner/06_tracing_a_langgraph_agent/) | Zero-code tracing of the ReAct agent from langgraph lesson 23 |
| 07 | [beginner_checkpoint_project](01_beginner/07_beginner_checkpoint_project/) | **Checkpoint:** Traced Multi-Step Pipeline |

## Intermediate: datasets, evaluation, prompts

| # | Lesson | Concept |
|---|--------|---------|
| 08 | [dataset_upload](02_intermediate/08_dataset_upload/) | Building a small RAG app, uploading a dataset of examples |
| 09 | [running_an_experiment](02_intermediate/09_running_an_experiment/) | `evaluate()`, running the RAG app over a dataset |
| 10 | [custom_evaluators](02_intermediate/10_custom_evaluators/) | Writing a per-example evaluator function |
| 11 | [summary_evaluators](02_intermediate/11_summary_evaluators/) | Aggregate metrics across a whole experiment |
| 12 | [pairwise_experiments](02_intermediate/12_pairwise_experiments/) | Comparing two experiments head to head |
| 13 | [prompt_hub](02_intermediate/13_prompt_hub/) | `pull_prompt`/`push_prompt`, versioned prompts |
| 14 | [prompt_engineering_lifecycle](02_intermediate/14_prompt_engineering_lifecycle/) | Iterate on a prompt, re-run the experiment, compare |
| 15 | [playground_experiments](02_intermediate/15_playground_experiments/) | Reading experiment results back from the SDK |
| 16 | [intermediate_checkpoint_project](02_intermediate/16_intermediate_checkpoint_project/) | **Checkpoint:** Dataset + Evaluator for the RAG App |

## Advanced: feedback, production monitoring

| # | Lesson | Concept |
|---|--------|---------|
| 17 | [publishing_feedback](03_advanced/17_publishing_feedback/) | `create_feedback`, user and LLM-as-judge scores on live runs |
| 18 | [filtering_and_dashboards](03_advanced/18_filtering_and_dashboards/) | Querying runs with filters, building a dashboard view |
| 19 | [online_evaluation](03_advanced/19_online_evaluation/) | Rules that auto-evaluate a sample of production traffic |
| 20 | [regression_testing_in_ci](03_advanced/20_regression_testing_in_ci/) | Comparing an experiment's score against a baseline, failing a build |
| 21 | [tracing_the_langgraph_agent_in_production](03_advanced/21_tracing_the_langgraph_agent_in_production/) | Metadata, tags, and feedback on the agent from langgraph lesson 32 |
| 22 | [cost_latency_and_scale](03_advanced/22_cost_latency_and_scale/) | Token usage, latency, and cost fields on a run |
| 23 | [advanced_capstone_project](03_advanced/23_advanced_capstone_project/) | **Capstone:** Fully Instrumented Agent, Dataset, Evaluator, Feedback Loop |
