# Lesson 17: Minimal Evaluation, Chunk vs. Graph Retrieval

## Where we left off

Every lesson since Lesson 2 has argued, by example, that graph
traversal beats chunk-based similarity search on multi-hop questions.
This lesson replaces "by example" with a number: **precision@k**, this
course's version of `naive_rag` Lesson 17's metric, computed twice, once
for chunk-based retrieval and once for graph-based retrieval, over the
same small labeled set of multi-hop questions.

## What precision@k means here

Same definition as `naive_rag` Lesson 17: given questions paired with
the source documents a correct answer needs, precision@k asks what
fraction of those needed documents actually get retrieved. This
lesson's twist is what counts as "retrieved" differs by method:

- **Chunk-based**: embed the question, rank every fixture note by
  cosine similarity, check whether the top-`k` results include the
  documents the question needs (`naive_rag`'s exact mechanism, reused
  unmodified as this lesson's baseline).
- **Graph-based**: find a starting node by embedding similarity
  (Lesson 10), traverse two hops, check whether the gathered facts'
  provenance (Lesson 12) covers the documents the question needs.

## The labeled set

```python
LABELED_QUESTIONS = [
    ("Who recalibrated the sensor that Dev flagged as drifting, and what tool did they use?",
     {"greenhouse.md", "maintenance-log.md"}),
    ("What project inspired Dev's soil moisture sensor, and in which room does that project happen?",
     {"soil-moisture-project.md", "workshop.md"}),
    ...
]
```

Every question in this set was deliberately built the same way Lesson
2's question was: the two needed documents share almost no vocabulary
with each other, only a connecting entity. That's not cherry-picking in
the unfair sense, it's the honest scope of the claim: this lesson
measures whether graph traversal wins specifically on the kind of
question this whole course exists for, not on questions any method
could get right unassisted.

## The code, piece by piece

```python
def precision_at_k_chunks(questions, store, k=2) -> float:
    hits = 0
    for query, needed_sources in questions:
        retrieved = retrieve_chunks(query, store, k)
        retrieved_sources = {r["source"] for r in retrieved}
        hits += needed_sources.issubset(retrieved_sources)
    return hits / len(questions)


def precision_at_k_graph(questions, graph, provenance, max_hops=2) -> float:
    hits = 0
    for query, needed_sources in questions:
        start = find_starting_node(query, graph)
        facts = gather_facts(graph, start, max_hops)
        covered_sources = set().union(*(provenance.get(n, set()) for n in nodes_touched(facts)))
        hits += needed_sources.issubset(covered_sources)
    return hits / len(questions)
```

Both functions score the same way, "did the needed sources actually get
surfaced," they just differ in *how* each method surfaces sources: one
by similarity ranking, one by traversal reaching a node that
provenance ties back to the right document.

## Running it

```bash
uv run python lessons/graph_rag/02_intermediate/17_minimal_evaluation_chunk_vs_graph/lesson.py
```

## Expected output

```
Chunk-based precision@2 (naive retrieval):
  [MISS] '...recalibrated the sensor...' -> needed {'greenhouse.md', 'maintenance-log.md'}, got {'greenhouse.md', 'soil-moisture-project.md'}
  ...
  Score: 0.20 (1/5)

Graph-based precision@2 hops (traversal):
  [HIT ] '...recalibrated the sensor...' -> needed {'greenhouse.md', 'maintenance-log.md'}, covered {'greenhouse.md', 'maintenance-log.md', ...}
  ...
  Score: 0.80 (4/5)
```

Exact scores shift with extraction and embedding variance, the gap
shouldn't: graph-based retrieval should clearly outscore chunk-based
retrieval on this labeled set, precisely because every question here
was built to need a connection chunk-based retrieval structurally can't
make.

## Why this doesn't generalize (yet)

See `naive_rag` Lesson 17's "Why this doesn't generalize (yet)" section
for the full argument; it applies here without modification: five
labeled questions is enough to demonstrate the *mechanism* of
precision@k, not enough to trust the exact number, and any
hyperparameter (this course's traversal depth, `naive_rag`'s similarity
threshold) must be tuned against a signal separate from the one you
report a final score on.

That second point is worth restating precisely for this course: Lesson
14's traversal depth was chosen by directly observing what each depth
retrieves for a hand-picked example question, not by nudging `max_hops`
until this lesson's precision@k score hit its highest value. If it had
been tuned against *this* labeled set instead, the score reported above
would no longer measure whether graph retrieval generalizes, it would
just describe how well the depth was fit to the five questions also
being used to grade it, exactly the contamination trap `naive_rag`
Lesson 17 warns about.

## Checkpoint

- Chunk-based and graph-based retrieval get scored by the same metric,
  precision@k, differing only in what counts as "retrieved."
- A labeled set built specifically around multi-hop, low-vocabulary-
  overlap questions measures the honest scope of Graph RAG's advantage,
  not an inflated one.
- Traversal depth (Lesson 14) was tuned before this lesson's score
  existed, against a different signal, so this score isn't contaminated
  by the same trap `naive_rag` Lesson 17 names.
- Five questions still isn't enough to trust the exact numbers, only
  enough to see the direction of the gap clearly.

**Try this yourself:** add a sixth labeled question of your own,
built from two fixture files that share almost no vocabulary but do
share a connecting entity. Does graph-based retrieval still find it?
Does chunk-based retrieval still miss it?

If anything here still feels unclear, ask before moving to Lesson 18.
