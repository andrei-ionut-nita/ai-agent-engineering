# Phase A: Author the `adaptive_rag` course

**Status: planned, not started.** This is a draft syllabus - present it to
the user for approval before writing any lesson files. Mirrors
[`../naive_rag/phase-a-authoring.md`](../naive_rag/phase-a-authoring.md)'s
structure and conventions exactly - only the content differs.

**Sequencing note**: this is the series' closing/synthesis course - its
Advanced tier explicitly wires in implementations from courses 2-5
(Hybrid, Graph, Corrective, Agentic RAG). The syllabus below can be
drafted and approved now, but Lessons 21 and 25 can't actually be *built*
until those courses exist. Don't start writing this course's lesson files
until courses 2-5 are authored (Phase A done for each) - revisit the plan
then in case anything about their real implementations changes what this
course routes to.

## To-Do List

- [ ] Get user approval on this syllabus before writing any files
- [ ] Do not begin authoring until courses 2-5 (`hybrid_rag`, `graph_rag`,
      `corrective_rag`, `agentic_rag`) have completed their own Phase A
- [ ] Before starting Lesson 21, confirm courses 1-5 all actually
      implement the shared `Strategy` protocol (`docs/RAG-SERIES-PLAN/README.md`,
      `ingest(docs) -> State` / `ask(query, state, k) -> str`) in their own
      Lesson 22/23 - if any course drifted from it, reconcile that course's
      signature before Lesson 21 tries to wire it in, don't silently
      special-case it inside the router.
- [ ] Lesson 17 references `naive_rag` L17's "Why this doesn't generalize
      (yet)" section (sample-size limits, tune/eval contamination) instead
      of re-deriving it - this course's routing rules (L4-L6) are tuned
      against the mixed question set, and L17's own evaluation reports a
      score on that same set, so this course is the series' clearest case
      of the contaminated pattern the README convention warns about.
      Either grow the labeled set enough that tune and eval can be split,
      or say so explicitly in L17 rather than presenting "routing wins" as
      more certain than it is.
- [ ] Decide whether `lessons/adaptive_rag/fixtures/` reuses
      `naive_rag`'s notes (now the most battle-tested fixture set in the
      series, since it's already used for multi-hop and confidently-wrong
      demos) or needs a superset covering every prior course's failure
      shape in one place
- [ ] Scaffold `lessons/adaptive_rag/` structure (tier folders, lesson
      folders, course-level `README.md`)
- [ ] Write Beginner tier (9 lessons): classifying query complexity,
      routing between 2-3 strategies, measuring whether routing helps
- [ ] Write Intermediate tier (9 lessons): confidence-aware routing,
      fallback, agentic tool-based routing, cost/latency tradeoffs,
      failure modes, minimal eval, checkpoint
- [ ] Write Advanced tier (8 lessons): multi-signal routing, a cheap
      pre-filter, wiring in real Advanced-tier implementations from
      courses 2-5, refactor, service wrapper, capstone, closing
      retrospective (no bridge lesson - this is the last course)
- [ ] No new dependency expected (this course composes prior courses'
      techniques and dependencies rather than introducing new ones) -
      confirm this holds once lessons are drafted
- [ ] Add the `adaptive_rag` course bullet to the repo root `README.md`
- [ ] Spot-check every lesson's `lesson.py` actually runs against a real
      `GOOGLE_API_KEY` and matches its README's "Expected output"

## Course 7 Spec: Adaptive RAG

- **Repo folder**: `lessons/adaptive_rag/`
- **Portfolio slug**: `adaptive-rag`
- **Title**: "Adaptive RAG: Routing Each Question to the Right Strategy"
- **Topic** (portfolio): `Retrieval` (existing value, no catalog edit
  needed)
- **Model**: Gemini (`GOOGLE_API_KEY`), used both for query-complexity
  classification (structured prompting) and for generation, same
  account/API surface as every prior course.
- **New dependency**: none expected - this course is a synthesis of
  courses 1-5's techniques, not a new mechanic of its own.
- **Relationship to prior courses**: this is the series' capstone course.
  Its entire premise is that no single strategy from courses 1-5 is
  always right - Lesson 2 recaps what each of the five prior courses is
  good and bad at before introducing routing as the unifying idea.

### Lesson breakdown (26 lessons across 3 tiers, draft)

**Beginner - classifying and routing between strategies (9 lessons)**
1. What Adaptive RAG is: not every question needs the same retrieval strategy
2. Recap: what naive, hybrid, graph, corrective, and agentic retrieval are each good and bad at
3. Classifying query complexity by hand: prompting Gemini to label a question simple-factual / multi-hop / ambiguous
4. Routing to a strategy based on the label: simple → naive retrieval, multi-hop → graph traversal
5. A single-tier router: two strategies, one classifier, one dispatch function
6. Adding a third route: ambiguous questions → corrective retrieval (grade-and-retry)
7. Measuring whether routing helps: routed vs. always-naive on a mixed question set
8. End-to-end: one script classifying and routing across three strategies
9. Beginner checkpoint: a CLI Q&A that routes each question to the right strategy automatically

**Intermediate - robust routing (9 lessons)**
10. Confidence-aware routing: what to do when the classifier itself is unsure
11. Falling back: retrying with a different strategy when the first one's result is graded low-confidence
12. Combining routing with agentic tool use: letting the model choose the strategy itself as a tool call, instead of a separate classifier step
13. Persisting routing decisions and outcomes for later analysis
14. Cost/latency tradeoffs: routing to the cheapest sufficient strategy, not always the most powerful one
15. Prompting for answers that disclose which strategy was used and why
16. Failure modes: misclassification sending a multi-hop question down the naive path, and vice versa
17. Minimal evaluation: precision@k and cost/latency, routed vs. each fixed strategy alone, on a mixed labeled question set
18. Intermediate checkpoint: a notes assistant that adaptively routes and reports which strategy it used

**Advanced - wiring in the real series, and a capstone (8 lessons)**
19. Where a single classifier-then-route step breaks down: multi-signal routing (query length, keyword density, entity count) instead of one LLM call
20. A lightweight rule-based pre-filter before the LLM classifier, to save a call on obviously-simple questions
21. Wiring in real Advanced-tier implementations from courses 2-5 (chromadb-backed naive/hybrid/graph/corrective, tool-based agentic) behind the router - straightforward specifically because all five already share the series' `Strategy` protocol (`ingest(docs) -> State` / `ask(query, state, k) -> str`), so this lesson composes five conforming implementations rather than reconciling five bespoke ones
22. A clean `route()` + strategy-registry pattern (name → strategy function)
23. Wrapping it as a small callable service (FastAPI) exposing one `/ask` endpoint that adapts internally
24. Instrumenting the service: logging which strategy handled each request and why
25. Advanced capstone: a complete adaptive RAG service combining every strategy from the series behind one endpoint
26. Series retrospective: how the seven courses build on each other, no code - a closing lesson (not a bridge to another course, since this is the last one)

Numbers/exact count may shift once READMEs are drafted, same caveat as
prior courses' syllabi.

## File Tree (`lessons/adaptive_rag/`, draft)

```
lessons/adaptive_rag/
├── README.md
├── 01_beginner/
│   ├── 01_what_is_adaptive_rag/
│   ├── 02_recap_of_the_series_strategies/
│   ├── 03_classifying_query_complexity/
│   ├── 04_routing_by_label/
│   ├── 05_a_single_tier_router/
│   ├── 06_adding_a_corrective_route/
│   ├── 07_measuring_whether_routing_helps/
│   ├── 08_end_to_end_adaptive_qa/
│   └── 09_beginner_checkpoint_project/
├── 02_intermediate/
│   ├── 10_confidence_aware_routing/
│   ├── 11_falling_back_on_low_confidence/
│   ├── 12_agentic_tool_based_routing/
│   ├── 13_persisting_routing_decisions/
│   ├── 14_cost_and_latency_tradeoffs/
│   ├── 15_prompting_for_disclosed_strategy_choice/
│   ├── 16_failure_modes_of_misrouting/
│   ├── 17_minimal_evaluation_routed_vs_fixed/
│   └── 18_intermediate_checkpoint_project/
├── 03_advanced/
│   ├── 19_multi_signal_routing/
│   ├── 20_a_rule_based_pre_filter/
│   ├── 21_wiring_in_the_real_series_strategies/
│   ├── 22_a_route_and_strategy_registry_pattern/
│   ├── 23_wrapping_it_as_a_service/
│   ├── 24_instrumenting_strategy_choice/
│   ├── 25_advanced_capstone_project/
│   └── 26_series_retrospective/
└── fixtures/
```

## Execution Steps (draft, mirrors `naive_rag`)

1. Confirm courses 2-5 have completed their own Phase A before starting
   this one (see Sequencing note above).
2. Present this syllabus to the user and get approval before writing any
   lesson files.
3. Decide the fixture strategy (see To-Do List above).
4. Scaffold `lessons/adaptive_rag/` matching `lessons/naive_rag/`'s
   structure exactly.
5. Write the lessons tier by tier, spot-checking `uv run python
   lessons/adaptive_rag/<tier>/<lesson>/lesson.py` against a real
   `GOOGLE_API_KEY` as each tier completes. Lesson 21 in particular
   should import/reuse the real functions from courses 2-5's Advanced
   tiers rather than reimplementing them.
6. Update repo-wide files:
   - Root `README.md`: add the `adaptive_rag` course bullet (the 7th and
     final course in the series).
7. Run `uv sync` and do a final full read-through pass of the new course
   folder.

## Verification

Every lesson's `lesson.py` actually runs and produces the output
documented in its README's "Expected output" section. Lesson 17's
evaluation should show routing beating (or at least matching) the best
single fixed strategy on the mixed question set - if it doesn't, the
classifier prompt or routing rules likely need adjusting so the lesson's
point actually lands. Lesson 25's capstone should demonstrably call each
of the five prior strategies at least once across its demo questions.
