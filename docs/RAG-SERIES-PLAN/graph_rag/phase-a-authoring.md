# Phase A: Author the `graph_rag` course

**Status: authored, partially verified.** All 26 lessons are written,
`lesson.py` files all pass `python -m py_compile`, and Lessons 1-10, 19,
20, and 26 (18 of 26) actually ran against the real Gemini API and
matched their README's expected output during authoring. Lessons 11-18
and 21-25 are written and internally consistent (same helper functions,
prompts, and patterns already proven live in Lessons 1-10/21) but were
not run against the live API in this session: the project's
`gemini-3.5-flash-lite` free-tier key hit its
`GenerateRequestsPerDayPerProjectPerModel-FreeTier` daily quota (500
requests/day) partway through authoring Lesson 11 and never recovered
before authoring finished. Embedding calls (`gemini-embedding-001`)
were unaffected and kept working throughout. Once the quota resets (or
a paid key is used), re-run each unverified lesson with `uv run python
lessons/graph_rag/<tier>/<lesson>/lesson.py` and confirm output against
its README's "Expected output" section; see the report handed back to
the user for the exact list.

This is distinct from the existing `lessons/pggraph` course, which
teaches the Postgres AGE extension, not the Graph RAG architecture. This
course is scoped to knowledge-graph-based retrieval and does not
duplicate pggraph's Postgres/Cypher content.

## To-Do List

- [x] Get user approval on this syllabus before writing any files
- [x] Lesson 23's `ingest()`/`ask()` implements the series' shared
      `Strategy` protocol (`docs/RAG-SERIES-PLAN/README.md`): `ingest(docs)
      -> State` where `State` here is `(graph, chroma_collection)`,
      `ask(query, state, k) -> str`. Say explicitly in that lesson's
      README what lives inside `State`, so `adaptive_rag` L21 can wire
      this in without reading the full implementation.
- [x] Lesson 17 references `naive_rag` L17's "Why this doesn't generalize
      (yet)" section (sample-size limits, tune/eval contamination) instead
      of re-deriving it. Lesson 14 (limiting traversal depth) must say
      explicitly whether that tuning is done against a held-out signal or
      against the same labeled set L17 reports the score on.
- [x] Lesson 16 (failure modes) treats extraction-error compounding
      across hops as its primary content, not one bullet among several -
      it's the field's actual central hard problem (a wrong or missed
      triple at hop 1 silently corrupts every answer that depends on hop
      2), and the course's credibility rests on demonstrating it visibly,
      not just naming it.
- [x] Lesson 24 (FastAPI wrapper) stays a short recipe reusing
      `naive_rag` L24's pattern almost verbatim rather than re-teaching
      FastAPI from scratch - keep it brief and let Lesson 16's
      error-compounding demo carry the depth this course is actually
      about.
- [x] Decide whether `lessons/graph_rag/fixtures/` reuses/extends
      `naive_rag`'s notes (which already have deliberate cross-references
      good for multi-hop questions - e.g. garden/weather-station,
      bookshelf/cello-practice/weather-station sharing a study) or needs
      its own set. Lean toward a fresh small fixture set scoped to this
      course, consistent with `hybrid_rag`'s decision, but the existing
      cross-reference *pattern* should carry over since multi-hop needs
      it.
      Decision: fresh fixture set written at `lessons/graph_rag/fixtures/notes/`
      (six notes: workshop, greenhouse, electronics-bench,
      soil-moisture-project, maintenance-log, book-club), with deliberate
      low-vocabulary-overlap, entity-linked multi-hop cross-references
      (e.g. greenhouse.md + maintenance-log.md share the humidity sensor
      entity but almost no wording).
- [x] Scaffold `lessons/graph_rag/` structure (tier folders, lesson
      folders, course-level `README.md`)
- [x] Write Beginner tier (9 lessons): entity/relation extraction by
      hand, a hand-rolled graph, traversal, multi-hop Q&A
- [x] Write Intermediate tier (9 lessons): graph+vector combined
      retrieval, entity normalization, persistence, depth limits,
      failure modes, minimal eval, checkpoint
- [x] Write Advanced tier (8 lessons): scale limits of a hand-rolled
      graph, `networkx`, graph+chromadb hybrid retrieval, refactor,
      service wrapper, capstone, series bridge lesson
- [x] Add `networkx` to `pyproject.toml`; run `uv sync`
- [x] Add the `graph_rag` course bullet to the repo root `README.md`
- [~] Spot-check every lesson's `lesson.py` actually runs against a real
      `GOOGLE_API_KEY` and matches its README's "Expected output".
      Done for Lessons 1-10, 19, 20, 26 (18/26); blocked for the rest by
      the free-tier daily quota on `gemini-3.5-flash-lite` being
      exhausted mid-session - see the Status line above for the exact
      remaining list and what to re-run once quota resets.

## Course 3 Spec: Graph RAG

- **Repo folder**: `lessons/graph_rag/`
- **Portfolio slug**: `graph-rag`
- **Title**: "Graph RAG: Answering Multi-Hop Questions with a Knowledge Graph"
- **Topic** (portfolio): `Retrieval` (existing value, no catalog edit
  needed)
- **Model**: Gemini (`GOOGLE_API_KEY`), used both for entity/relation
  extraction (structured prompting for `(subject, relation, object)`
  triples) and for generation, same as every other course in the series.
- **New dependency**: `networkx` (pure Python, no server) for the
  Advanced-tier graph. `chromadb` is reused for the vector half of the
  Advanced-tier graph+vector hybrid retrieval.
- **Relationship to prior courses**: this course's whole premise is the
  specific failure `naive_rag` Lesson 16 demonstrated (a multi-hop
  question that single-shot top-k retrieval can't answer because the
  needed facts live in two different chunks). Lesson 2 recaps that
  failure directly before introducing graphs as the fix.

### Lesson breakdown (26 lessons across 3 tiers, draft)

**Beginner - extracting and traversing a graph by hand (9 lessons)**
1. What Graph RAG is: multi-hop questions that chunk retrieval can't answer
2. Recap: watching naive/hybrid retrieval fail on a multi-hop question (reusing `naive_rag` Lesson 16's failure demo)
3. Extracting entities from text by hand (prompting Gemini for a list of named entities per chunk)
4. Extracting relationships between entities (prompting for `(subject, relation, object)` triples)
5. Building a graph by hand: nodes and edges as a Python adjacency dict
6. Graph traversal by hand: one-hop and two-hop neighbor lookup
7. Answering a multi-hop question: traverse the graph to gather connected facts, then generate
8. End-to-end: one script extracting a mini knowledge graph from the fixtures and answering a multi-hop question
9. Beginner checkpoint: a CLI that builds a graph from a folder of notes and answers connection questions

**Intermediate - making the graph practical (9 lessons)**
10. Combining graph traversal with vector retrieval: embed the query to find a starting entity, then traverse from there
11. Handling ambiguous entity mentions (the same entity referred to differently across notes) with simple normalization
12. Multi-document graphs: merging entities and relations extracted across several files into one graph
13. Persisting the graph to disk (JSON) instead of re-extracting every run
14. Limiting traversal depth, and why unbounded hops pull in irrelevant context
15. Prompting for grounded, cited multi-hop answers (citing which hop each fact came from)
16. Failure modes, foregrounding error compounding: a wrong or missed relation at hop 1 silently corrupts every multi-hop answer that depends on hop 2, shown visibly with a deliberately broken extraction; also traversal that stops one hop short of what's needed
17. Minimal evaluation: precision@k on multi-hop questions, chunk-based retrieval vs. graph-based retrieval
18. Intermediate checkpoint: the notes-search assistant upgraded with graph-based multi-hop answers and citations

**Advanced - graduating the graph, and a capstone (8 lessons)**
19. Where a hand-rolled adjacency-dict graph breaks down at scale
20. Introducing `networkx` as a drop-in graph library
21. Re-pointing extraction/traversal at `networkx`, same interface as Lessons 6-7
22. Combining `networkx` traversal with `chromadb` vector search as one graph+vector hybrid retrieval step
23. Refactoring the pipeline into reusable functions (`ingest()`, `ask()`)
24. Wrapping it as a small callable service (FastAPI, matching `naive_rag` Lesson 24's pattern)
25. Advanced capstone: a complete graph RAG service over a folder of documents, with citations and documented limitations
26. Where Graph RAG hits a wall - a short bridge lesson naming the failure modes that motivate Corrective RAG (sets up course 4, no code)

Numbers/exact count may shift once READMEs are drafted, same caveat as
prior courses' syllabi.

## File Tree (`lessons/graph_rag/`, draft)

```
lessons/graph_rag/
├── README.md
├── 01_beginner/
│   ├── 01_what_is_graph_rag/
│   ├── 02_where_naive_retrieval_fails_multi_hop/
│   ├── 03_extracting_entities_by_hand/
│   ├── 04_extracting_relationships_by_hand/
│   ├── 05_building_a_graph_by_hand/
│   ├── 06_graph_traversal_by_hand/
│   ├── 07_answering_a_multi_hop_question/
│   ├── 08_end_to_end_graph_qa/
│   └── 09_beginner_checkpoint_project/
├── 02_intermediate/
│   ├── 10_combining_graph_and_vector_retrieval/
│   ├── 11_normalizing_ambiguous_entities/
│   ├── 12_multi_document_graphs/
│   ├── 13_persisting_the_graph/
│   ├── 14_limiting_traversal_depth/
│   ├── 15_prompting_for_cited_multi_hop_answers/
│   ├── 16_failure_modes_of_graph_retrieval/
│   ├── 17_minimal_evaluation_chunk_vs_graph/
│   └── 18_intermediate_checkpoint_project/
├── 03_advanced/
│   ├── 19_where_hand_rolled_graphs_break_down/
│   ├── 20_introducing_networkx/
│   ├── 21_repointing_traversal_at_networkx/
│   ├── 22_graph_and_chromadb_hybrid_retrieval/
│   ├── 23_refactoring_into_ingest_and_ask/
│   ├── 24_wrapping_it_as_a_service/
│   ├── 25_advanced_capstone_project/
│   └── 26_where_graph_rag_hits_a_wall/
└── fixtures/
```

## Execution Steps (draft, mirrors `naive_rag`)

1. Present this syllabus to the user and get approval before writing any
   lesson files.
2. Design and write `lessons/graph_rag/fixtures/` with deliberate
   multi-hop connections (see To-Do List above).
3. Scaffold `lessons/graph_rag/` matching `lessons/naive_rag/`'s structure
   exactly.
4. Write the lessons tier by tier, spot-checking `uv run python
   lessons/graph_rag/<tier>/<lesson>/lesson.py` against a real
   `GOOGLE_API_KEY` as each tier completes.
5. Update repo-wide files:
   - `pyproject.toml`: add `networkx`.
   - Root `README.md`: add the `graph_rag` course bullet.
6. Run `uv sync` and do a final full read-through pass of the new course
   folder.

## Verification

Every lesson's `lesson.py` actually runs and produces the output
documented in its README's "Expected output" section; `uv sync` succeeds
after the `networkx` dependency add. Lesson 17's precision@k comparison
should show graph-based retrieval clearly beating chunk-based retrieval
specifically on the multi-hop questions in the labeled set - if it
doesn't, the fixture cross-references or labeled questions likely need
adjusting so the lesson's point actually lands.
