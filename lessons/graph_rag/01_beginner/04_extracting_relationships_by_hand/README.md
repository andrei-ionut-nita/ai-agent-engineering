# Lesson 4: Extracting Relationships Between Entities

## Where we left off

Lesson 3 pulled entities out of a document, a list of who and what it
mentions. A list of entities alone isn't a graph yet, though, it's just
a bag of nouns with no structure between them. What actually makes
something a *graph* is the edges: the relationships connecting one
entity to another. This lesson extracts those, as `(subject, relation,
object)` **triples**, the standard shape a knowledge graph edge takes.

## Why triples, specifically

You might assume any free-text description of a relationship would do,
"Mia used the multimeter to recalibrate the sensor" is perfectly
readable. The reason to force it into `(subject, relation, object)`
instead is mechanical, not stylistic: a triple is *traversable*. Given
the triple `("Mia", "recalibrated", "humidity sensor")`, code can ask
"what did Mia recalibrate?" or "who recalibrated the humidity sensor?"
by pattern-matching on a fixed position, subject or object. A sentence
of free text can't be queried that way without re-running language
understanding on it every single time you want to ask a different
question of it. The triple pays that understanding cost once, at
extraction time, so every later traversal is just a lookup.

## The code, piece by piece

```python
prompt = f"""...list every relationship between two entities as
a (subject, relation, object) triple...

Return ONLY a JSON array of 3-element arrays, like:
[["Mia", "recalibrated", "humidity sensor"], ...]

Text:
{text}"""
```

Same JSON-mode pattern as Lesson 3, applied to a slightly harder
extraction task: instead of "list the nouns," this asks the model to
also identify the *verb phrase* connecting two of those nouns, and to
keep that verb phrase short and consistent (a few words, not a full
sentence), so triples about the same kind of relationship end up
comparable to each other later.

```python
triples = extract_relationships(text)
```

Notice what this does *not* do yet: it doesn't merge these triples with
any other document's triples, or build an actual graph structure out of
them. That's Lesson 5. This lesson's whole job is turning one document's
prose into a flat list of `(subject, relation, object)` triples,
nothing more.

## Running it

```bash
uv run python lessons/graph_rag/01_beginner/04_extracting_relationships_by_hand/lesson.py
```

## Expected output

```
--- maintenance-log.md ---
[('Mia', 'recalibrated', 'humidity sensor'), ('Dev', 'flagged', 'humidity sensor'), ('Mia', 'pulled', 'multimeter'), ('multimeter', 'kept in', 'garage bench'), ...]
```

Exact wording of the relation strings varies slightly run to run (a
model might say "recalibrated" one time and "fixed" the next for the
same fact), the same non-determinism Lesson 3 already flagged, now one
level deeper: it affects both endpoints of an edge *and* its label.

## Checkpoint

- **Triple**: a `(subject, relation, object)` edge, the unit a knowledge
  graph is built from.
- Triples are traversable by pattern-matching on a fixed position
  (subject or object); free-text sentences aren't, without re-running
  language understanding every time.
- Extraction still turns unstructured prose into structure at the cost
  of some inconsistency (relation labels don't always match verbatim
  across runs or documents), a limitation this course confronts head-on
  starting in Lesson 11.

**Try this yourself:** run this lesson against `soil-moisture-project.md`
and look specifically for a triple connecting it back to
`workshop.md`'s content (Mia's lumber-drying log). Does the model
produce one, even though the two ideas appear in the same document but
several sentences apart? That's the exact kind of edge Lesson 7's
multi-hop traversal will depend on later.

If anything here still feels unclear, ask before moving to Lesson 5.
