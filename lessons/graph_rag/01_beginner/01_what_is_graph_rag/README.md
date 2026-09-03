# Lesson 1: What Is Graph RAG, and Why Do Multi-Hop Questions Need It?

## Where we left off

If you've done this repo's `naive_rag` course, you already built the
baseline RAG loop by hand: chunk a document, embed the chunks, retrieve
the ones closest in meaning to a question, hand them to Gemini. That
loop is powerful, and it has a specific, structural blind spot: it
treats every question as "find the single best matching passage (or the
top few)." It has no notion that the answer to a question might not
live in any one passage at all, but in the *connection* between two
passages that don't otherwise resemble each other.

**Graph RAG** is the fix. Instead of (or alongside) chunks in a vector
store, it extracts entities (people, places, things) and relationships
between them (`subject, relation, object` triples) into a knowledge
graph, then answers a question by traversing that graph from a starting
entity, hopping across relationships to gather facts that live in
different documents, before generating an answer.

## The question this lesson asks

*"Who recalibrated the sensor that Dev flagged as drifting in the
greenhouse, and what tool did they use?"*

Notice the shape of this question: it isn't answerable from one
sentence, or even one document. Answering it correctly requires knowing
that Dev flagged a humidity sensor as drifting (one fact, one document),
that a specific person recalibrated it afterward (a second fact, a
different document), and what tool that person reached for while doing
it (a third fact, possibly a third document). A single best-matching
chunk, however good the embedding, can only ever hand you one of those
facts at a time.

## The code, piece by piece

```python
response = client.models.generate_content(model=CHAT_MODEL, contents=QUESTION)
```

Same raw Gemini call as `naive_rag` Lesson 1: ask the question with no
retrieved context at all, no document, nothing. Gemini has never seen
this household's notes, so it can only guess, or admit it doesn't know.
That's expected, and it's not really the point of this lesson, unlike
in `naive_rag` Lesson 1. The point here is what comes next.

Even *with* Naive RAG's chunk-and-retrieve loop bolted on, this
particular question would still be hard: the words "recalibrated,"
"Dev," "flagged," "drifting," and "tool" don't all cluster in the same
document, or even in the same *pair* of documents an embedding search
would naturally group together. Lesson 2 proves this concretely by
running last course's actual retrieval pipeline against this exact
question and watching it come up short.

## Running it

```bash
uv run python lessons/graph_rag/01_beginner/01_what_is_graph_rag/lesson.py
```

## Expected output

```
Question: Who recalibrated the sensor that Dev flagged as drifting in the greenhouse, and what tool did they use?

Gemini, with no context:
<a guess, or an "I don't know" - varies each run>

Graph RAG's shape, built one piece at a time starting next lesson:
  1. Extract  - pull (subject, relation, object) triples out of each document
  2. Build    - assemble those triples into a graph of entities and relationships
  3. Traverse - starting from an entity in the question, hop across relationships
  4. Generate - hand the facts gathered along the way to Gemini alongside the question
```

If instead you see an error, check the
[Troubleshooting section](../../../../README.md#troubleshooting) in
this project's root README.

## Checkpoint

- **Graph RAG**: extract entities and relationships into a knowledge
  graph, then answer questions by traversing across relationships
  instead of (or in addition to) ranking chunks by similarity.
- **Multi-hop question**: a question whose answer requires connecting
  facts that live in different documents, via a shared entity, rather
  than any single passage containing the whole answer.
- Why this matters: Naive RAG's top-k similarity search has no concept
  of "go find a second, connected fact." Graph RAG's traversal step is
  built specifically to do that.

**Try this yourself:** before reading Lesson 2, guess which two of this
course's six fixture notes (in `lessons/graph_rag/fixtures/notes/`) you
think contain the two halves of this lesson's question. Skim the
folder, then check yourself once Lesson 3 starts extracting from them.

If anything here still feels unclear, ask before moving to Lesson 2.
