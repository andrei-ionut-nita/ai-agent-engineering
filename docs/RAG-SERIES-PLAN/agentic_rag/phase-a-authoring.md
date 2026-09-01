# Phase A: Author the `agentic_rag` course

**Status: planned, not started.** This is a draft syllabus - present it to
the user for approval before writing any lesson files. Mirrors
[`../naive_rag/phase-a-authoring.md`](../naive_rag/phase-a-authoring.md)'s
structure and conventions exactly - only the content differs.

Note: the repo's `lessons/langchain` course already teaches agents
generically via a framework. This course is framework-free (raw Gemini
function calling) and specifically about retrieval-as-a-tool: when an
agent should retrieve, how many times, and what else it should be able to
call instead. Scope it to avoid re-teaching general agent concepts
`langchain` already covers.

## To-Do List

- [ ] Get user approval on this syllabus before writing any files
- [ ] Lesson 23's `tools()`/`run_agent()` implements the series' shared
      `Strategy` protocol (`docs/RAG-SERIES-PLAN/README.md`) at its
      outer boundary: `ingest(docs) -> State` where `State` here is
      `(chroma_collection, tool_registry)`, `ask(query, state, k) -> str`
      wrapping `run_agent()` internally. Say explicitly in that lesson's
      README what lives inside `State`, so `adaptive_rag` L21 can wire
      this in without reading the full implementation.
- [ ] Lesson 17 references `naive_rag` L17's "Why this doesn't generalize
      (yet)" section (sample-size limits, tune/eval contamination) instead
      of re-deriving it.
- [ ] Lesson 16 (failure modes) covers malformed or erroring tool calls
      (bad arguments, a tool that raises) as a distinct case from
      unnecessary retrieval or non-converging loops - function-calling
      APIs fail this way often enough in practice that skipping it would
      leave a real gap, not just an edge case.
- [ ] Lesson 24 (FastAPI wrapper) stays a short recipe reusing
      `naive_rag` L24's pattern almost verbatim rather than re-teaching
      FastAPI from scratch - keep it brief and let Lesson 16's failure
      modes carry the depth this course is actually about.
- [ ] Confirm `google-genai`'s function-calling / tool-use API surface
      (exact method names, `types.Tool`/`FunctionDeclaration` shapes) for
      the installed SDK version before drafting Lesson 3 - this is the
      one genuinely new API surface this course introduces beyond what
      `naive_rag` already used.
- [ ] Decide on the second, non-retrieval tool used in Lessons 7-9
      (e.g. a simple calculator or a date/time lookup) - pick something
      trivial enough not to need its own new dependency.
- [ ] Scaffold `lessons/agentic_rag/` structure (tier folders, lesson
      folders, course-level `README.md`)
- [ ] Write Beginner tier (9 lessons): function-calling basics, retrieval
      as a tool, deciding whether to retrieve, multi-tool agents
- [ ] Write Intermediate tier (9 lessons): multi-step loops, query
      planning/decomposition, iteration bounds, failure modes, minimal
      eval, checkpoint
- [ ] Write Advanced tier (8 lessons): tool-registry pattern, optional
      cross-reference to Corrective RAG's grading as a tool, refactor,
      service wrapper, capstone, series bridge lesson
- [ ] No new dependency expected (Gemini's native function calling is
      part of `google-genai`, already in `pyproject.toml`) - confirm this
      holds once lessons are drafted
- [ ] Add the `agentic_rag` course bullet to the repo root `README.md`
- [ ] Spot-check every lesson's `lesson.py` actually runs against a real
      `GOOGLE_API_KEY` and matches its README's "Expected output"

## Course 5 Spec: Agentic RAG

- **Repo folder**: `lessons/agentic_rag/`
- **Portfolio slug**: `agentic-rag`
- **Title**: "Agentic RAG: Retrieval as a Tool the Model Chooses to Use"
- **Topic** (portfolio): `Retrieval` (existing value, no catalog edit
  needed)
- **Model**: Gemini (`GOOGLE_API_KEY`), using its native function-calling
  support to let the model request tool calls, same account/API surface
  as every prior course, one new capability of it (tool declarations).
- **New dependency**: none expected.
- **Relationship to prior courses**: every prior course in the series
  hardcodes retrieval as a fixed pipeline step. This course's premise is
  that retrieval should be a *choice* the model makes, like any other
  tool - Lesson 2 recaps that fixed-pipeline assumption directly before
  loosening it.

### Lesson breakdown (26 lessons across 3 tiers, draft)

**Beginner - retrieval as a tool the model can call (9 lessons)**
1. What Agentic RAG is: retrieval as a tool the model chooses to call, not a hardcoded pipeline step
2. Recap: the fixed retrieve-then-generate pipeline every prior course used, and its assumption that retrieval is always needed
3. Gemini function calling basics: declaring a tool, letting the model request a call
4. Wrapping retrieval as a callable tool the model can request
5. A single-step agent loop: model call → tool call (if requested) → tool result → final answer
6. Deciding not to retrieve: questions the model can answer from context or its own knowledge without calling the tool
7. Multi-tool agents: adding a second, non-retrieval tool alongside retrieval
8. End-to-end: one script where the agent picks retrieval, the other tool, or neither, per question
9. Beginner checkpoint: a CLI assistant that decides per-question what (if anything) to call

**Intermediate - multi-step reasoning and bounded loops (9 lessons)**
10. Multi-step loops: an agent that calls retrieval more than once for one question
11. Query planning: letting the agent decompose a compound question into sub-queries, each retrieved separately
12. Passing tool results back into context correctly, and why naive concatenation breaks down over multiple steps
13. Persisting conversation and tool-call history across a multi-turn session
14. Bounding iterations: a max-steps guard so the loop always terminates
15. Prompting for grounded, cited answers when multiple retrieval calls each contributed different facts
16. Failure modes: the agent retrieving unnecessarily, looping without converging on an answer, and a tool call that comes back malformed or errors outright (the agent has to handle a failed call, not just a successful one)
17. Minimal evaluation: how often the agent calls retrieval when it's actually needed vs. skips it inappropriately, on a labeled question set
18. Intermediate checkpoint: a multi-turn notes assistant that retrieves only when needed, across a conversation

**Advanced - a clean agent loop, and a capstone (8 lessons)**
19. Where a hand-rolled if/elif tool-dispatch loop breaks down as more tools are added
20. Structuring the loop into a clean `run_agent()` function, separating loop logic from tool implementations
21. A tool-registry pattern (name → function mapping) replacing if/elif chains, and adding a third tool
22. Optional: wiring in Corrective RAG's grading step as one of the agent's tools (cross-reference, not a hard dependency on that course existing yet)
23. Refactoring into `tools()` + `run_agent()` functions
24. Wrapping it as a small callable service (FastAPI, single-turn or streaming)
25. Advanced capstone: a complete agentic RAG assistant with multiple tools, multi-step reasoning, and citations
26. Where Agentic RAG hits a wall - a short bridge lesson naming the failure modes that motivate Multimodal RAG (sets up course 6, no code)

Numbers/exact count may shift once READMEs are drafted, same caveat as
prior courses' syllabi.

## File Tree (`lessons/agentic_rag/`, draft)

```
lessons/agentic_rag/
├── README.md
├── 01_beginner/
│   ├── 01_what_is_agentic_rag/
│   ├── 02_the_fixed_pipeline_assumption/
│   ├── 03_gemini_function_calling_basics/
│   ├── 04_retrieval_as_a_tool/
│   ├── 05_a_single_step_agent_loop/
│   ├── 06_deciding_not_to_retrieve/
│   ├── 07_multi_tool_agents/
│   ├── 08_end_to_end_agent_qa/
│   └── 09_beginner_checkpoint_project/
├── 02_intermediate/
│   ├── 10_multi_step_loops/
│   ├── 11_query_planning_and_decomposition/
│   ├── 12_passing_tool_results_back_correctly/
│   ├── 13_persisting_conversation_history/
│   ├── 14_bounding_iterations/
│   ├── 15_prompting_for_cited_multi_call_answers/
│   ├── 16_failure_modes_of_agentic_retrieval/
│   ├── 17_minimal_evaluation_retrieve_or_not/
│   └── 18_intermediate_checkpoint_project/
├── 03_advanced/
│   ├── 19_where_if_elif_dispatch_breaks_down/
│   ├── 20_structuring_run_agent/
│   ├── 21_a_tool_registry_pattern/
│   ├── 22_optional_corrective_grading_as_a_tool/
│   ├── 23_refactoring_into_tools_and_run_agent/
│   ├── 24_wrapping_it_as_a_service/
│   ├── 25_advanced_capstone_project/
│   └── 26_where_agentic_rag_hits_a_wall/
└── fixtures/
```

## Execution Steps (draft, mirrors `naive_rag`)

1. Present this syllabus to the user and get approval before writing any
   lesson files.
2. Confirm the `google-genai` function-calling API shape and pick the
   second tool (see To-Do List above).
3. Scaffold `lessons/agentic_rag/` matching `lessons/naive_rag/`'s
   structure exactly.
4. Write the lessons tier by tier, spot-checking `uv run python
   lessons/agentic_rag/<tier>/<lesson>/lesson.py` against a real
   `GOOGLE_API_KEY` as each tier completes.
5. Update repo-wide files:
   - Root `README.md`: add the `agentic_rag` course bullet.
6. Run `uv sync` and do a final full read-through pass of the new course
   folder.

## Verification

Every lesson's `lesson.py` actually runs and produces the output
documented in its README's "Expected output" section. Lesson 17's
evaluation should show the agent correctly skipping retrieval on
questions answerable without it, and correctly calling it (possibly more
than once) on questions that need it - if it doesn't, the labeled question
set or tool descriptions likely need adjusting.
