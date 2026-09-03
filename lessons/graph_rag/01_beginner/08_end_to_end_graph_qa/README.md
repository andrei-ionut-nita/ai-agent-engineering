# Lesson 8: End-to-End Graph QA

## Where we left off

Lessons 3 through 7 each built one piece: extract entities, extract
relationships, build a graph, traverse it, generate an answer. Lesson 7
ran that pipeline against three hand-picked fixture files. This lesson
removes the hand-picking: it extracts from *all six* of this course's
fixture notes into one graph, then answers the multi-hop question by
traversing that full graph, the same way a real system would, where you
don't get to curate which documents are "the relevant ones" ahead of
time, extraction has to happen over everything.

## What's actually new here

Nothing conceptually. This is deliberately a consolidation lesson, not
a new-idea lesson, the same role `naive_rag` Lesson 8 played for that
course. The one thing worth noticing: extracting from all six documents
means the graph now also contains Priya's book club, the workshop's
lumber log, and the soil moisture project, entities entirely unrelated
to the humidity sensor question. Traversal from `"humidity sensor"`
still only follows the edges that are actually there, so none of that
unrelated content shows up in the gathered facts unless a real edge
connects to it. That's the graph doing its job: growing the corpus
doesn't dilute a specific traversal's precision the way it would dilute
a naive top-k similarity search across a larger, noisier document set.

## The code, piece by piece

```python
def build_graph_from_notes(notes_dir: Path) -> Graph:
    graph: Graph = {}
    for path in sorted(notes_dir.glob("*.md")):
        text = path.read_text()
        for subject, relation, obj in extract_relationships(text):
            add_edge(graph, subject, relation, obj)
    return graph
```

This one function is Lessons 3-5 collapsed together: read every
fixture, extract triples from each, add them all into one shared graph.
Extraction runs once per file, six calls total, and every file's
triples land in the same dictionary, so an edge extracted from
`maintenance-log.md` and an edge extracted from `electronics-bench.md`
that happen to share a node (like `"multimeter"`) are now connected in
one graph, even though neither file, alone, mentions the other file's
content.

## Running it

```bash
uv run python lessons/graph_rag/01_beginner/08_end_to_end_graph_qa/lesson.py
```

## Expected output

```
Building graph from 6 fixture notes...
Graph has <N> nodes.

Question: Who recalibrated the sensor that Dev flagged as drifting in the greenhouse, and what tool did they use?

Answer:
Mia recalibrated the humidity sensor that Dev flagged. <possibly a
brief, honest hedge on the exact tool connection, same as Lesson 7>
```

## Checkpoint

- Scaling extraction to every document in a folder, rather than a
  hand-picked few, is exactly what a real system has to do; this lesson
  is the first time this course does that.
- A graph's traversal precision doesn't degrade just because the graph
  as a whole got bigger, unlike similarity search, which has to rank a
  question against every chunk in a growing corpus, traversal only ever
  follows edges that actually exist from wherever it starts.
- This is still a hand-rolled, in-memory graph, rebuilt by
  re-extracting from scratch every run. Lessons 12-13 fix the second
  half of that (merging and persisting), Lesson 19 confronts the first
  half (what happens when "in-memory adjacency dict" stops scaling).

**Try this yourself:** ask a second question this lesson doesn't try,
something that spans `book-club.md` and `electronics-bench.md`
(both mention the soldering station). Pick a starting entity yourself
and see whether two-hop traversal from it reaches everything the
question needs.

If anything here still feels unclear, ask before moving to Lesson 9.
