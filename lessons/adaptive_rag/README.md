# Course index

A linear, one-concept-per-lesson path through Adaptive RAG: not every
question needs the same retrieval strategy, so instead of picking one
architecture and running every question through it, this course classifies
each question first and routes it to whichever of this series' five prior
strategies actually fits. Built the same way as the rest of the series,
direct calls to Google's Gemini API (`google-genai`), no LangChain, no
LlamaIndex, only this time the retrieval strategies being routed to are
the real, already-verified implementations from courses 1-5. Do these in
order, top to bottom, each lesson folder has a `README.md` (read first)
and a `lesson.py` (run second). Don't move to the next lesson until the
current one's checkpoint questions feel solid.

This is the seventh and final course in a series organized by RAG
architecture (mirroring
[andreinita.co/learning/rag-fundamentals](https://andreinita.co/learning/rag-fundamentals/)'s
map of nine architectures) rather than by library like this repo's other
courses. It is the series' closing, synthesis course: its whole premise is
that no single strategy from `naive_rag`, `hybrid_rag`, `graph_rag`,
`corrective_rag`, or `agentic_rag` is always right, and its Advanced tier
wires all five of those courses' real Advanced-tier implementations in
behind one router, rather than teaching a sixth retrieval mechanic of its
own. `multimodal_rag` (course 6) is not wired in here; this course routes
between the five text-retrieval strategies that share the series' common
protocol.

You should complete `naive_rag`, `hybrid_rag`, `graph_rag`,
`corrective_rag`, and `agentic_rag` before starting this course. Lesson 2
recaps what each one is good and bad at, but that recap assumes you've
already built and watched each one fail firsthand, it isn't a substitute
for having done that.

Setup: `GOOGLE_API_KEY` in a `.env` file at the project root (get a free
key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)),
no Docker, no database, no extra account, no new dependency beyond what
courses 1-5 already installed. Then
`uv run python lessons/adaptive_rag/<NN>_<name>/lesson.py` from the
project root.

## Beginner: classifying and routing between strategies

| # | Lesson | Concept |
|---|--------|---------|
| 01 | [what_is_adaptive_rag](01_beginner/01_what_is_adaptive_rag/) | Not every question needs the same retrieval strategy |
| 02 | [recap_of_the_series_strategies](01_beginner/02_recap_of_the_series_strategies/) | What naive, hybrid, graph, corrective, and agentic retrieval are each good and bad at |
| 03 | [classifying_query_complexity](01_beginner/03_classifying_query_complexity/) | Prompting Gemini to label a question simple-factual / multi-hop / ambiguous |
| 04 | [routing_by_label](01_beginner/04_routing_by_label/) | Simple to naive retrieval, multi-hop to graph traversal |
| 05 | [a_single_tier_router](01_beginner/05_a_single_tier_router/) | Two strategies, one classifier, one dispatch function |
| 06 | [adding_a_corrective_route](01_beginner/06_adding_a_corrective_route/) | Ambiguous questions to corrective retrieval (grade-and-retry) |
| 07 | [measuring_whether_routing_helps](01_beginner/07_measuring_whether_routing_helps/) | Routed vs. always-naive on a mixed question set |
| 08 | [end_to_end_adaptive_qa](01_beginner/08_end_to_end_adaptive_qa/) | One script, classifying and routing across three strategies |
| 09 | [beginner_checkpoint_project](01_beginner/09_beginner_checkpoint_project/) | **Checkpoint:** CLI Q&A That Routes Automatically |

## Intermediate: robust routing

| # | Lesson | Concept |
|---|--------|---------|
| 10 | [confidence_aware_routing](02_intermediate/10_confidence_aware_routing/) | What to do when the classifier itself is unsure |
| 11 | [falling_back_on_low_confidence](02_intermediate/11_falling_back_on_low_confidence/) | Retrying with a different strategy when a result is graded low-confidence |
| 12 | [agentic_tool_based_routing](02_intermediate/12_agentic_tool_based_routing/) | Letting the model choose the strategy itself, as a tool call |
| 13 | [persisting_routing_decisions](02_intermediate/13_persisting_routing_decisions/) | Saving routing decisions and outcomes for later analysis |
| 14 | [cost_and_latency_tradeoffs](02_intermediate/14_cost_and_latency_tradeoffs/) | Routing to the cheapest sufficient strategy, not always the most powerful one |
| 15 | [prompting_for_disclosed_strategy_choice](02_intermediate/15_prompting_for_disclosed_strategy_choice/) | Answers that disclose which strategy was used and why |
| 16 | [failure_modes_of_misrouting](02_intermediate/16_failure_modes_of_misrouting/) | Misclassification sending a multi-hop question down the naive path, and back |
| 17 | [minimal_evaluation_routed_vs_fixed](02_intermediate/17_minimal_evaluation_routed_vs_fixed/) | Precision@k and cost/latency, routed vs. each fixed strategy, on a mixed labeled set |
| 18 | [intermediate_checkpoint_project](02_intermediate/18_intermediate_checkpoint_project/) | **Checkpoint:** Notes Assistant That Reports Its Own Routing |

## Advanced: wiring in the real series, and a capstone

| # | Lesson | Concept |
|---|--------|---------|
| 19 | [multi_signal_routing](03_advanced/19_multi_signal_routing/) | Query length, keyword density, entity count, instead of one LLM call |
| 20 | [a_rule_based_pre_filter](03_advanced/20_a_rule_based_pre_filter/) | A cheap filter before the LLM classifier, to save a call on obviously-simple questions |
| 21 | [wiring_in_the_real_series_strategies](03_advanced/21_wiring_in_the_real_series_strategies/) | The real Advanced-tier `ingest()`/`ask()` from courses 1-5, composed behind the router |
| 22 | [a_route_and_strategy_registry_pattern](03_advanced/22_a_route_and_strategy_registry_pattern/) | A clean `route()` plus a name-to-strategy registry |
| 23 | [wrapping_it_as_a_service](03_advanced/23_wrapping_it_as_a_service/) | A small FastAPI `/ask` endpoint that adapts internally |
| 24 | [instrumenting_strategy_choice](03_advanced/24_instrumenting_strategy_choice/) | Logging which strategy handled each request, and why |
| 25 | [advanced_capstone_project](03_advanced/25_advanced_capstone_project/) | **Capstone:** A Complete Adaptive RAG Service |
| 26 | [series_retrospective](03_advanced/26_series_retrospective/) | How the seven courses build on each other, no code, the series' closing lesson |
