# Lesson 2: Watching Naive Retrieval Fail on a Multi-Hop Question

## Where we left off

Lesson 1 claimed that Naive RAG's chunk-and-retrieve loop struggles with
multi-hop questions. This lesson doesn't ask you to take that on faith,
it runs the actual retrieval mechanics (embed, rank by cosine
similarity, take the top `k`) against this course's own fixture notes
and this course's own multi-hop question, live, so you watch it come up
short yourself. This mirrors exactly what `naive_rag` Lesson 16 did with
its own fixtures: same failure, same underlying cause, new example.

## Why this happens, not just that it happens

It's tempting to assume the fix is simply "increase `k`." Lesson 16 of
`naive_rag` already showed that helps *sometimes*, when the two needed
pieces happen to also be each other's next-best semantic match. This
lesson's question is deliberately built so that assumption fails harder:
the two documents that together answer it, `greenhouse.md` (Dev flagged
a sensor as drifting) and `maintenance-log.md` (Mia recalibrated it with
a multimeter) don't share much vocabulary. "Drifting," "flagged,"
"greenhouse," and "peppers" don't appear anywhere near "recalibrated,"
"multimeter," or "connector." An embedding model captures *meaning*
well, but two documents can be topically connected through a real-world
event (the same sensor, at two points in time) while using almost none
of the same words or concepts to describe it. Cosine similarity has no
way to know these two chunks are about the same sensor unless the text
itself makes that connection legible.

This is the misconception worth naming directly: it's easy to assume
"retrieval failed" means "the embedding model is bad" or "`k` was too
small." Neither is true here. The embedding model is doing exactly what
it's supposed to, ranking by *semantic* similarity to the question. The
question just isn't answerable that way, because the two facts it needs
aren't semantically close to each other, they're *causally* close: one
event, described two different ways, in two different documents,
written days apart by different people. That's a relationship, not a
similarity, and similarity search has no mechanism for relationships at
all.

## The code, piece by piece

```python
retrieved = retrieve(QUESTION, store, k=2)
```

This is `naive_rag`'s exact retrieval function: embed the question,
embed every fixture note, rank by cosine similarity, keep the top `k`.
Nothing new here, the point is running unmodified Naive RAG mechanics
against a question they were never designed to answer.

```python
retrieved_files = [r["source"] for r in retrieved]
needed = {"greenhouse.md", "maintenance-log.md"}
got_both = needed.issubset(set(retrieved_files))
```

The check that makes the failure concrete: did the top-`k` results
include *both* of the documents the question actually needs, not just
one of them, and not just a document that happens to mention the
greenhouse in passing.

## Running it

```bash
uv run python lessons/graph_rag/01_beginner/02_where_naive_retrieval_fails_multi_hop/lesson.py
```

## Expected output

```
Question: Who recalibrated the sensor that Dev flagged as drifting in the greenhouse, and what tool did they use?

k=2 retrieved: ['greenhouse.md', '<some other file>']
  Got both needed documents? False

k=4 retrieved: ['greenhouse.md', 'maintenance-log.md', '<...>', '<...>']
  Got both needed documents? True

Answer with k=2 (partial context):
<either an honest "the context doesn't contain the answer," or a
partial guess that gets who flagged the sensor right but has no way to
know who recalibrated it or what tool they used>

Even when k is raised enough to include both documents (as with k=4), a
much larger fraction of the retrieved context ends up irrelevant to the
question compared to a graph traversal that follows the specific
relationship connecting the two facts. Raising k is a blunt fix:
it works by including more of everything, not by understanding which
two documents the question actually needs.
```

Exact filenames retrieved at `k=2` vary slightly by embedding run, but
`maintenance-log.md` reliably fails to make the cut until `k` is raised
well past what a two-fact question should need.

## Checkpoint

- Multi-hop failures aren't caused by a bad embedding model or too small
  a `k`, they're caused by similarity search having no mechanism for
  *relationships* between facts, only for *closeness in meaning*.
- Two documents can be connected by a real-world event while sharing
  almost no vocabulary, exactly the case similarity search is blind to.
- Raising `k` is a blunt fix, it papers over the specific missing
  connection by including everything, at the cost of retrieving much
  more irrelevant context along with it.
- This is precisely the gap Graph RAG's traversal step exists to close:
  follow the actual relationship (the same sensor, two documents),
  rather than hoping semantic similarity happens to bridge it.

If anything here still feels unclear, ask before moving to Lesson 3.
