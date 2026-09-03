# Lesson 16: Failure Modes of Graph Retrieval

## Where we left off

Every lesson since Lesson 7 has shown Graph RAG working. This lesson is
the course's pedagogical centerpiece, and it exists to show, live, the
one way Graph RAG actually breaks in practice, not a minor rough edge,
but the field's real central hard problem: **error compounding across
hops**. A wrong or missed triple at hop 1 doesn't just cost you that one
fact, it silently corrupts every answer that depends on reaching hop 2
through it.

## The misconception this lesson corrects

It's natural to assume a graph traversal either works or visibly fails,
the way a missing file throws an error. You might picture a bad
extraction as something you'd *notice*, a triple that's obviously
wrong, a node that's obviously missing. That's not what actually
happens. Watch this lesson's first demo closely: the corrupted graph
below doesn't crash, doesn't warn, doesn't print anything different
about *how* it's answering. `gather_facts` runs exactly the same code,
on exactly the same starting node, for exactly the same number of hops,
and returns a perfectly well-formed list of facts, just missing the one
that mattered. The corruption is invisible at every layer except the
final answer, which quietly gets worse without anything else in the
system objecting.

## Demonstration 1: a wrong extraction at hop 1

```python
def corrupt_graph(graph: Graph) -> Graph:
    corrupted = {node: list(edges) for node, edges in graph.items()}
    # Simulate a real extraction failure: the model missed (or
    # mis-extracted) the edge connecting Dev's flag to the sensor,
    # exactly the kind of silent miss that happens on real documents
    # when a sentence's subject is implied rather than stated.
    corrupted["humidity sensor"] = [
        (relation, other)
        for relation, other in corrupted.get("humidity sensor", [])
        if "Dev" not in other and "flagged" not in relation
    ]
    corrupted["Dev"] = [
        (relation, other)
        for relation, other in corrupted.get("Dev", [])
        if "flagged" not in relation
    ]
    return corrupted
```

This deletes exactly one real-world fact from an otherwise-correct
graph, the edge recording that Dev flagged the humidity sensor. Nothing
else changes. Run the same question through the correct graph and the
corrupted one, side by side, and watch what happens: the correct graph
still connects Mia and the multimeter to the sensor just fine (that
edge wasn't touched), but the corrupted graph's *answer* degrades in a
way that has nothing obviously to do with the one deleted edge, it
simply can no longer confirm Dev's role, or in some runs, hedges the
entire answer more heavily, because one thread connecting the story
together is gone. That's error compounding: hop 1's damage doesn't stay
contained to hop 1, it propagates into how confidently (or correctly)
every later hop's fact gets used.

## Demonstration 2: traversal that stops one hop short

```python
for depth in (1, 2):
    facts = gather_facts(graph, "humidity sensor", max_hops=depth)
    answer = generate_answer(QUESTION, facts)
```

This is Lesson 14's depth knob, revisited with a sharper point: at
`max_hops=1`, traversal from `"humidity sensor"` reaches Dev's flag and
Mia's recalibration (both one hop out), but never reaches the
multimeter, which is two hops out (`humidity sensor -> Mia ->
multimeter`). The answer at depth 1 correctly names Mia but has no way
to mention the tool at all, not because the fact doesn't exist in the
graph, but because traversal stopped exactly one hop short of it. This
is a different failure than Demonstration 1: nothing is wrong with the
graph itself, the depth setting simply didn't reach far enough for this
specific question.

## Why this is worse than Naive RAG's failure modes

`naive_rag` Lesson 16's failures (a multi-hop question needing two
chunks, a fact split across a chunk boundary) are visible in the
retrieved *text* itself, if you print what got retrieved, the gap is
right there to see. Graph RAG's extraction-error failure is not visible
in anything this course has printed so far: the traversal code runs
without error, the gathered facts list looks completely normal, only
the final answer's *content* reveals anything went wrong, and even
then, only if you already know the right answer to compare against.
This is precisely why the field treats extraction quality as the
central hard problem of Graph RAG: a retrieval failure you can see is a
problem you can debug; a retrieval failure that looks identical to
success until you fact-check it by hand is a much harder one.

## Running it

```bash
uv run python lessons/graph_rag/02_intermediate/16_failure_modes_of_graph_retrieval/lesson.py
```

## Expected output

```
--- Demonstration 1: a wrong/missing extraction at hop 1 ---

Answer (correct graph):
Based on the provided facts:
* Who recalibrated the sensor: Mia recalibrated the humidity sensor (which Dev noticed and flagged).
* What tool they used: the facts do not name a specific calibration tool, but do state Mia pulled a multimeter.

Answer (corrupted graph, Dev's flag silently removed):
Based on the provided facts, Mia recalibrated the humidity sensor. However, the facts do not mention what tool she used for the recalibration.

--- Demonstration 2: traversal that stops one hop short ---

depth=1: ...there is no mention of any tool used for the recalibration, so that detail isn't supported by the facts.
depth=2: Mia recalibrated the humidity sensor (which Dev noticed and flagged). While the facts mention that Mia... pulled a multimeter..., the specific tool used for the recalibration isn't explicitly named in the list.
```

Exact wording varies between runs; what should hold steady is the
*shape* of both failures: Demonstration 1's corrupted answer loses
specifically the fact that traced through the deleted edge, nothing
else; Demonstration 2's depth-1 answer loses specifically the fact that
lived exactly one hop further out than traversal reached.

## Checkpoint

- **Error compounding**: a wrong or missing triple at hop 1 doesn't stay
  contained, it silently degrades every answer whose reasoning needs to
  pass through that hop, with no error, warning, or visible sign in the
  traversal code itself.
- A graph retrieval failure is *harder* to notice than a Naive RAG
  retrieval failure, because the gathered facts still look completely
  well-formed, only the final answer's content, checked against ground
  truth, reveals the gap.
- Traversal stopping one hop short of the answer is a separate, simpler
  failure from extraction error: the graph is fine, the depth setting
  just wasn't enough for this particular question.
- This is why extraction quality (Lessons 3-4's whole premise) isn't a
  Beginner-tier detail to move past quickly, it's the load-bearing
  assumption this entire architecture depends on.

**Try this yourself:** write a second, different corruption: instead of
deleting the Dev-flagged edge, *mutate* the multimeter fact to say Mia
used a "screwdriver" instead. Run the same question through this
version. Is this failure easier or harder to notice than
Demonstration 1's, and why might a subtly wrong fact be more dangerous
in practice than a missing one?

If anything here still feels unclear, ask before moving to Lesson 17.
