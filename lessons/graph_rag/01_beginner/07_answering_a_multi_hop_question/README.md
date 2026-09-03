# Lesson 7: Answering a Multi-Hop Question

## Where we left off

Every piece is now on the table: extraction (Lessons 3-4), a graph
(Lesson 5), and traversal (Lesson 6). This lesson assembles them into
the thing this whole course has been building toward: given a
question, find a starting entity mentioned in it, traverse outward to
gather connected facts, and hand those facts to Gemini to generate a
grounded answer. This is Graph RAG's version of Naive RAG's
retrieve-then-generate loop, with traversal standing in for similarity
search.

## Why "start from an entity in the question" works

You might assume the graph needs to be searched exhaustively, checking
every node to see if it's relevant. It doesn't, and this is worth
understanding precisely: a question names its own starting point. "Who
recalibrated the sensor that Dev flagged as drifting in the
greenhouse?" mentions "sensor" and "greenhouse" directly. Pick either
one as the starting node (this lesson uses "humidity sensor," found by
a simple keyword match against the graph's node names, a technique
Lesson 10 replaces with something sturdier), then traverse outward.
Two hops from "humidity sensor" reaches "greenhouse" (one hop), "Mia,"
"Dev," and "multimeter" (via the reverse edge back from the sensor and
onward), which is precisely the set of facts the question needs, without
ever having to inspect the parts of the graph about Priya's book club
or Mia's woodworking log.

## The code, piece by piece

```python
def gather_facts(graph: Graph, start: str, max_hops: int = 2) -> list[str]:
    facts = []
    frontier = {start}
    for _ in range(max_hops):
        next_frontier = set()
        for node in frontier:
            for relation, other in graph.get(node, []):
                facts.append(f"{node} {relation} {other}")
                next_frontier.add(other)
        frontier = next_frontier
    return facts
```

This is a slightly more general version of Lesson 6's `two_hop`: instead
of a fixed two nested loops, it walks outward one "frontier" (the set of
nodes reached so far) at a time, for `max_hops` rounds. Each fact gets
turned into a plain sentence (`f"{node} {relation} {other}"`), because
that's a format Gemini can read directly in a prompt, same idea as
turning retrieved chunks into prompt text in `naive_rag`.

```python
context = "\n".join(facts)
prompt = f"""Answer the question using only the facts below...

Facts:
{context}

Question: {query}"""
```

Structurally identical to `naive_rag`'s generation step, the only
difference is *what* fills in `context`: traversed graph facts instead
of retrieved chunks of prose. Generation itself doesn't need to know or
care which kind of retrieval produced its input.

## Running it

```bash
uv run python lessons/graph_rag/01_beginner/07_answering_a_multi_hop_question/lesson.py
```

## Expected output

```
Question: Who recalibrated the sensor that Dev flagged as drifting in the greenhouse, and what tool did they use?

Facts gathered by traversal (starting from 'humidity sensor'):
  humidity sensor (reverse) flagged Dev
  humidity sensor (reverse) recalibrated Mia
  Dev flagged humidity sensor
  Mia recalibrated humidity sensor
  Mia pulled multimeter
  ...

Answer:
Based on the provided facts, Mia recalibrated the humidity sensor that
Dev flagged. The facts also show Mia pulled a multimeter around the
same time, though they don't explicitly state she used it for the
recalibration itself, so that part is left as a reasonable but
unconfirmed connection rather than a stated fact.
```

Compare this directly against Lesson 2's `k=2` result for the exact
same question: that attempt returned "the context doesn't contain the
answer," with zero correct information. This lesson gets the actual
who right, correctly, using a fraction of the raw text Lesson 2's `k=4`
fallback needed, because traversal followed the real relationship
instead of hoping semantic similarity would surface both documents
together. Notice, too, that it's honest about the one connection (which
tool, exactly) the graph's edges don't fully nail down, an edge for
"Mia recalibrated the sensor" and a separate edge for "Mia pulled the
multimeter" are two different facts, not proof they happened in the
same motion. That caution is a preview of Lesson 15's grounded-citation
work: a good multi-hop answer should only claim what its edges actually
support.

## Checkpoint

- Graph RAG's retrieve-then-generate loop: find a starting entity in the
  question, traverse outward to gather connected facts, generate from
  those facts, exactly parallel to Naive RAG's embed-retrieve-generate
  loop.
- A question names its own starting point; traversal doesn't need to
  search the whole graph, only walk outward from there.
- Generation doesn't care whether its input came from similarity search
  or graph traversal, it just needs facts formatted as readable text.

**Try this yourself:** change the starting entity from `"humidity
sensor"` to `"Dev"` and rerun. Does traversal still reach Mia and the
multimeter within two hops? If not, how many hops does it actually
take, and what does that tell you about how much the choice of starting
entity matters?

If anything here still feels unclear, ask before moving to Lesson 8.
