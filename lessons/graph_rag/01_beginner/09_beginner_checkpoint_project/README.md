# Lesson 9: Beginner Checkpoint - Graph Q&A CLI

## What this is

No new concepts in this lesson. This is a checkpoint: a small, real
script built entirely out of ideas from Lessons 1 through 8, combined
into one thing. If you can read `lesson.py` and understand why every
piece is there, you've mastered the Beginner tier. If any piece feels
unfamiliar, that's a sign to revisit the lesson it came from before
continuing to Intermediate.

## What it does

Builds one knowledge graph from every fixture note in
`lessons/graph_rag/fixtures/notes/` (six short Markdown files about a
household's greenhouse, garage workshop, shared electronics bench, and
more), then answers three questions, each requiring a different number
of hops across the graph, printing the whole run so you can see
traversal reach further for a harder question and stop sooner for an
easier one.

## Where each piece came from

```python
def build_graph(notes_dir: Path) -> Graph:
    graph: Graph = {}
    for path in sorted(notes_dir.glob("*.md")):
        for subject, relation, obj in extract_relationships(path.read_text()):
            add_edge(graph, subject, relation, obj)
    return graph
```
Lesson 8, unchanged: extract from every fixture, merge every triple into
one shared graph.

```python
facts = gather_facts(graph, start_entity, max_hops)
```
Lesson 7's traversal, unchanged: walk outward from a starting entity,
collecting every edge encountered within `max_hops` hops.

```python
answer = generate_answer(query, facts)
```
Lesson 7's generation, unchanged: turn gathered facts into a grounded
answer, honest about what the facts don't establish.

```python
def ask(query: str, graph: Graph, start_entity: str, max_hops: int = 2) -> str:
    facts = gather_facts(graph, start_entity, max_hops)
    return generate_answer(query, facts)
```
The whole pipeline as one function call, this course's first `ask()`,
the same shape `naive_rag` Lesson 8 introduced for its own pipeline.

## Running it

```bash
uv run python lessons/graph_rag/01_beginner/09_beginner_checkpoint_project/lesson.py
```

You should see three questions answered: one one-hop question (what's
on the electronics bench), one two-hop multi-hop question (this
course's running greenhouse-sensor example), and one that traces
inspiration between two different rooms in the house (the soil moisture
project's connection back to the workshop's lumber log), each pulled
correctly out of a graph merged from six fixture files with no
project-by-project hint about which file holds which answer.

## Try this yourself

Without looking anything up:

- Change `max_hops` from 2 to 1 for the greenhouse-sensor question, does
  it still get answered, or does traversal stop one hop short of Mia
  and the multimeter?
- Pick a different starting entity for the same question (`"Dev"`
  instead of `"humidity sensor"`), does the answer come out the same?
- Add a fourth question of your own that needs the book club and
  the electronics bench connected (both mention the soldering
  station), and pick a starting entity for it yourself.

If you can make these changes confidently, you're ready for the
Intermediate tier, starting at Lesson 10.
