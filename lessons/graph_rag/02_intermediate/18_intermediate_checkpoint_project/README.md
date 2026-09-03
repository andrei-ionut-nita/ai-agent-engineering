# Lesson 18: Intermediate Checkpoint - Graph Q&A With Citations

## What this is

No new concepts in this lesson. This is a checkpoint: the Beginner
tier's CLI (Lesson 9) upgraded with every Intermediate-tier idea,
combined into one thing. If you can read `lesson.py` and explain why
every piece is there, you've mastered the Intermediate tier. If any
piece feels unfamiliar, revisit the lesson it came from before
continuing to Advanced.

## What it does

Builds a knowledge graph from every fixture note (persisting it to disk
so a second run skips extraction entirely), normalizes ambiguous entity
mentions, finds each question's starting node by embedding similarity
instead of a hand-typed constant, limits traversal to a depth chosen in
Lesson 14, and answers three multi-hop questions with per-hop
citations, printing the whole run.

## Where each piece came from

```python
if GRAPH_PATH.exists():
    graph, provenance = load_graph(GRAPH_PATH)
else:
    graph, provenance = build_graph_with_provenance(NOTES_DIR)
    normalize(graph, provenance)
    save_graph(graph, provenance, GRAPH_PATH)
```
Lessons 11-13, combined: extract with provenance tracking, normalize
duplicate entities, persist to disk so later runs load instead of
re-extracting.

```python
start = find_starting_node(query, graph)
```
Lesson 10, unchanged: pick a starting node by embedding similarity to
the question, not a hand-typed constant.

```python
facts = gather_facts_with_sources(graph, provenance, start, max_hops=MAX_HOPS)
```
Lesson 15's provenance-aware traversal, with `MAX_HOPS` set to the value
Lesson 14 justified by direct observation, not by score-chasing.

```python
def ask(query: str, graph: Graph, provenance: Provenance) -> str:
    start = find_starting_node(query, graph)
    facts = gather_facts_with_sources(graph, provenance, start, max_hops=MAX_HOPS)
    return generate_cited_answer(query, facts)
```
The whole Intermediate-tier pipeline as one function call, this
course's second `ask()`, now with citations folded directly into every
answer, matching this repo's `ask()` convention (Lesson 23 formalizes
this as the shared cross-course `Strategy` protocol).

## Running it

```bash
uv run python lessons/graph_rag/02_intermediate/18_intermediate_checkpoint_project/lesson.py
```

Run it twice: the first run builds and saves the graph; the second
loads it, skipping extraction entirely, and should answer noticeably
faster.

## Try this yourself

Without looking anything up:

- Delete the saved graph file and rerun with `MAX_HOPS` set to 1
  instead of 2. Which of the three questions, if any, still gets
  answered fully?
- Add a fourth question that needs `book-club.md` and
  `electronics-bench.md` connected (the soldering station), and check
  whether its citations correctly point at both files.
- Open the saved graph JSON directly and find the entry for
  `"electronics bench"`. Does its edge list include anything that
  originally came from `maintenance-log.md`'s mention of "garage
  bench," confirming Lesson 11's normalization actually ran?

If you can make these changes confidently, you're ready for the
Advanced tier, starting at Lesson 19.
