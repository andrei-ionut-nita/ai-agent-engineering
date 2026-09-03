# Lesson 15: Prompting for Grounded, Cited Multi-Hop Answers

## Where we left off

Every answer generated since Lesson 7 has been honest about what it
does and doesn't know, but not *specific* about which fact backed which
part of the answer. "Mia recalibrated the sensor, and the facts don't
confirm which tool" is honest, but if you wanted to double-check that
claim against the original documents, you'd have no pointer to where to
look. This lesson adds citations: for each hop the answer relies on,
which document did that fact actually come from.

## Why citing a hop is a different problem than citing a chunk

`naive_rag` Lesson 15 already taught citation: attribute a claim to the
source file a retrieved chunk came from. This lesson's version is
structurally harder, and it's worth seeing exactly why. A single
retrieved chunk has one obvious source, the file it was read from. A
multi-hop answer is built from *several* facts, gathered from
*different* hops, and (thanks to Lesson 12's provenance tracking) some
of those facts might themselves trace back to more than one document.
"Cite the source" now means "cite the source *for each hop*," not one
source for the whole answer, because a multi-hop claim can be right
about hop 1 and wrong about hop 2, and a single blanket citation
couldn't tell you which.

## The code, piece by piece

```python
def gather_facts_with_sources(
    graph: Graph, provenance: Provenance, start: str, max_hops: int = 2
) -> list[tuple[str, set[str]]]:
    facts = []
    frontier = {start}
    visited = {start}
    for _ in range(max_hops):
        next_frontier = set()
        for node in frontier:
            for relation, other in graph.get(node, []):
                sources = provenance.get(node, set()) & provenance.get(other, set())
                if not sources:
                    sources = provenance.get(node, set()) | provenance.get(other, set())
                facts.append((f"{node} {relation} {other}", sources))
                ...
```

Each gathered fact now carries its own source set, not just text. The
`&` (intersection) first tries the *strongest* possible attribution: a
source file that mentions *both* ends of this specific edge is almost
certainly where that edge was extracted from. Falling back to `|`
(union) when no single file mentions both ends handles edges created
during Lesson 11's normalization, where the two endpoints came from
different documents by design, in that case, the honest citation is
"this connection spans these documents," not a single file.

```python
context = "\n".join(f"{fact} [source: {', '.join(sources)}]" for fact, sources in facts)
prompt = f"""...cite the source file for each fact you use..."""
```

The sources ride along in the prompt text itself, right next to the
fact they belong to, so Gemini has everything it needs to attach a
citation to each claim without having to guess or invent one.

## Running it

```bash
uv run python lessons/graph_rag/02_intermediate/15_prompting_for_cited_multi_hop_answers/lesson.py
```

## Expected output

```
Question: Who recalibrated the sensor that Dev flagged as drifting in the greenhouse, and what tool did they use?

Answer:
Mia recalibrated the humidity sensor [maintenance-log.md].

The provided facts do not state what tool Mia used to recalibrate the
sensor.
```

Exact wording varies, the citations shouldn't: each claim should point
at the actual fixture file that fact traces back to, checkable directly
against the fixtures in `lessons/graph_rag/fixtures/notes/`.

## Checkpoint

- Citing a multi-hop answer means citing per hop, not once for the
  whole answer, since different hops can trace to different documents.
- Provenance tracking (Lesson 12) is what makes per-hop citation
  possible at all, a fact with no recorded source can't be cited
  honestly, only guessed at.
- When an edge spans two documents (a normalized, merged entity), the
  honest citation names both sources, not one arbitrarily chosen one.

**Try this yourself:** find a fact in this lesson's output whose source
set has more than one file in it. Open both files and confirm by hand
that the edge really is supported by content in both, not just one with
the other tagging along incorrectly.

If anything here still feels unclear, ask before moving to Lesson 16.
