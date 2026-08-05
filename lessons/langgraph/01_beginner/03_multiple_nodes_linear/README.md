# Lesson 3: A four-node pipeline, still just a straight line

## Where we left off

Lesson 2 chained two nodes. This lesson stretches that out to four, on
purpose, no new concept, just more wiring, so the mechanical pattern of
"a graph is nodes plus edges you draw yourself" fully sinks in before
Lesson 4 introduces the first real fork in the road.

## What we're building

A tiny text pipeline, the running theme for the rest of this tier: raw
input text gets cleaned, then split into words, then counted, then
formatted into a readable summary. Four small, single-purpose nodes,
each one doing exactly one thing, wired straight through in sequence.

## The code, piece by piece

```python
class GraphState(TypedDict):
    raw_text: str
    words: list[str]
    word_count: int
    summary: str
```

Four fields, one written by each node. None of them need a reducer,
each field is written by exactly one node in this graph, so plain
last-write-wins (Lesson 2's default) is all that's needed here.

```python
def clean_text(state: GraphState) -> dict:
    return {"raw_text": state["raw_text"].strip().lower()}


def split_words(state: GraphState) -> dict:
    return {"words": state["raw_text"].split()}


def count_words(state: GraphState) -> dict:
    return {"word_count": len(state["words"])}


def format_summary(state: GraphState) -> dict:
    return {"summary": f"{state['word_count']} words: {', '.join(state['words'])}"}
```

Four nodes, four single responsibilities. Notice each one only reads
the fields it needs (`split_words` doesn't care about `word_count`,
`count_words` doesn't care about `raw_text`) and only writes the one
field it's responsible for. This is a good habit generally: small nodes
that each do one obvious thing are far easier to test, reorder, and
debug than one giant node doing everything at once.

```python
builder.add_edge(START, "clean_text")
builder.add_edge("clean_text", "split_words")
builder.add_edge("split_words", "count_words")
builder.add_edge("count_words", "format_summary")
builder.add_edge("format_summary", END)
```

Five `add_edge` calls, one path, no branches. This is still exactly the
same idea as Lesson 1's `START -> shout -> END`, just with three more
stops along the way. The graph runs `clean_text`, then whatever it
returned feeds into `split_words`, and so on, in the exact order the
edges say, no more and no less.

## Running it

```bash
uv run python lessons/langgraph/01_beginner/03_multiple_nodes_linear/lesson.py
```

## Checkpoint

- **linear graph**: a chain of nodes with exactly one path from `START`
  to `END`, no branches, no loops.
- **single-purpose nodes**: each node in this lesson reads only what it
  needs and writes only the one field it owns, easier to reason about
  than one large node doing everything.
- **wiring order matters**: `add_edge` calls determine execution order,
  a node only runs once every edge pointing into it has been satisfied.

If anything here still feels unclear, ask before moving to Lesson 4.
