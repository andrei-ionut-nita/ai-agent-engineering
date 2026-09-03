# Lesson 11: Normalizing Ambiguous Entity Mentions

## Where we left off

Every graph built so far has a quiet bug hiding in it: this course's own
fixtures call the same physical workbench "electronics bench" in
`electronics-bench.md` and "garage bench" in `maintenance-log.md`. To a
human reading both files, these are obviously the same bench. To the
graph-building code from Lessons 5-10, they're two entirely different
nodes, because nothing in that code compares node *names* for
similarity, it only checks for exact string equality. This lesson fixes
that: normalizing entity mentions that refer to the same real-world
thing but were extracted under different names.

## Why this isn't a rare edge case

You might assume this is a fixture-specific quirk, unlikely to matter
much in practice. It's the opposite: this happens *constantly* with
LLM-based extraction, precisely because the model is extracting from
each document independently, with no memory of how it named something
in a different document five minutes ago. "Electronics bench" and
"garage bench" is a mild case, real corpora produce worse ones ("Q3
revenue," "third-quarter revenue," "revenue for Q3 2024") routinely.
Left unfixed, this silently fragments the graph: two nodes that should
be one mean any edge attached to only one of them is invisible to
traversal starting from the other, exactly the kind of quiet gap that's
easy to miss until a specific question happens to hit it.

## The code, piece by piece

```python
node_names = list(graph.keys())
node_vectors = embed_texts(node_names)

pairs_to_merge = []
for i, name_a in enumerate(node_names):
    for j, name_b in enumerate(node_names):
        if j <= i:
            continue
        if cosine_similarity(node_vectors[i], node_vectors[j]) >= MERGE_THRESHOLD:
            pairs_to_merge.append((name_a, name_b))
```

The same embedding tool this course has used since Lesson 10, pointed
at a new job: instead of comparing a *question* to node names, this
compares node names to *each other*, looking for pairs close enough in
meaning to plausibly be the same entity. `MERGE_THRESHOLD = 0.75` here
is a real number chosen by actually running this course's own graph and
observing that "electronics bench" and "garage bench" score around
`0.79`, clearly separated from every other, genuinely-different pair
(all scoring well under `0.6`). This is the same idea as `naive_rag`
Lesson 14's similarity floor, a threshold set by looking at what real
scores look like, not picked out of thin air.

```python
def merge_nodes(graph: Graph, keep: str, drop: str) -> None:
    for relation, other in graph.pop(drop, []):
        graph.setdefault(keep, []).append((relation, other))
    for node, edges in graph.items():
        graph[node] = [(rel, keep if other == drop else other) for rel, other in edges]
```

Merging means two things: move every edge the dropped node had onto the
node being kept, and rewrite every *other* node's edges so any edge
that used to point at the dropped name now points at the kept name
instead. Skip either half and the merge is incomplete, either the kept
node is missing edges the dropped one had, or some other node's edges
still dangle toward a name that no longer exists in the graph.

## Running it

```bash
uv run python lessons/graph_rag/02_intermediate/11_normalizing_ambiguous_entities/lesson.py
```

## Expected output

```
Nodes before normalizing: 45
Merging: 'electronics bench' -> 'garage bench' (similarity 0.79)
Merging: "garage bench's top drawer" -> 'garage bench' (similarity 0.79)
Merging: 'workshop side of the garage' -> 'garage bench' (similarity 0.76)
Merging: 'shared electronics bench' -> 'garage bench' (similarity 0.88)
Merging: 'tray of jumper wires' -> 'jumper wire tray' (similarity 0.94)
Merging: 'soil moisture sensor' -> 'humidity sensor' (similarity 0.76)
Merging: 'garage bench' -> 'back half of the garage' (similarity 0.81)
Nodes after normalizing: 38

Edges on 'back half of the garage' after normalizing:
  (reverse) takes up -> woodworking workshop
  holds -> multimeter
  ...
```

Exact node counts, which pairs cross the threshold, and even which
surviving name a chain of merges lands on can shift with extraction
variance, the underlying point doesn't: without this step, some of the
multimeter's real connections are reachable only through "garage
bench," invisible to any traversal that starts from "electronics bench"
instead. Because the demo prints edges for whichever name "electronics
bench" ultimately resolves to (it can get merged into "garage bench,"
which in turn gets merged into something else again), the code tracks
that chain explicitly rather than hardcoding a name that may no longer
exist in the graph after normalizing.

Note that a real run can also show a threshold false positive, like
"soil moisture sensor" merging into "humidity sensor" at 0.76, two
genuinely different sensors that happen to embed close together. This
isn't a bug: it's the "Try this yourself" lesson below arriving
unprompted, real thresholds aren't perfectly clean cutoffs, and this is
exactly the kind of borderline case worth checking by hand rather than
trusting blindly.

## Checkpoint

- **Entity normalization**: merging graph nodes that refer to the same
  real-world thing but were extracted under different names.
- This is a routine, not a rare, consequence of extracting from
  documents independently, expect it on any real corpus, not just this
  course's fixtures.
- A similarity threshold for merging should be set by looking at real
  score gaps on your own graph (Lesson 3's approach, reused), not
  guessed.
- An unmerged duplicate doesn't throw an error, it silently fragments
  the graph, edges attached to the "wrong" copy of an entity are simply
  unreachable from the other copy, with no warning that anything is
  missing.

**Try this yourself:** lower `MERGE_THRESHOLD` from `0.75` to `0.5` and
rerun. Which unrelated node pairs incorrectly get merged now (check for
merges that don't make sense, like "greenhouse" and "workshop")? This
is the flip side of the threshold-setting lesson: too low merges things
that shouldn't be merged, exactly the same shape of mistake as setting
`naive_rag` Lesson 14's similarity floor too loose.

If anything here still feels unclear, ask before moving to Lesson 12.
