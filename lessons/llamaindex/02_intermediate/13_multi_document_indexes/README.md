# Lesson 13: Multi-document indexes

## One index, several unrelated documents

Every earlier lesson indexed a small pile of related documents (the three
Nimbus policy files). This lesson makes explicit something those lessons
already did implicitly: `VectorStoreIndex.from_documents()` doesn't care
whether the documents it's given are related. It's just as happy indexing
two documents about *completely different things*, an internal
engineering handbook and a customer-facing product FAQ, in the same
index, and retrieval will still find the right Nodes for a given
question.

This is the common real-world shape: you don't usually build a separate
index per document type, you build one index over everything you have
(or everything relevant to a given user/scope), and let similarity search
sort out which document actually answers a given question. LangChain's
equivalent is the same idea: `Chroma.from_documents()` doesn't care what
kind of documents you hand it either, one vector store, arbitrary content.

## The fixture data

This lesson's own `data/` folder (pre-staged, read as-is):

- `engineering_handbook.txt`: internal process docs, code review rules,
  on-call rotation, deploy windows, testing requirements.
- `product_faq.txt`: customer-facing FAQ about the Cobalt-1 warehouse
  robot, battery life, flooring requirements, connectivity behavior,
  supervision ratio.

The two files share no topical overlap (nothing in the FAQ answers an
engineering-process question and vice versa), which makes it easy to
verify retrieval is actually distinguishing between them.

## Source attribution: `response.source_nodes`

Every `QueryEngine` response carries `.source_nodes`, the list of Nodes
actually used to synthesize the answer. Each Node's `.metadata["file_name"]`
(inherited from `SimpleDirectoryReader`, same as every lesson since
Lesson 2) tells you which source document it came from. This is how you
verify, after the fact, which document(s) backed a given answer, whether
by design (Lesson 11's filters) or, as here, by letting an unfiltered
search find the right document(s) on its own.

## `similarity_top_k` matters at small scale

This fixture is tiny on purpose, one Node per document, two Nodes total.
`as_query_engine()`'s default `similarity_top_k` is 2
(`llama_index.core.constants.DEFAULT_SIMILARITY_TOP_K`), which at this
scale would retrieve *both* documents on every question regardless of
relevance, hiding the thing worth demonstrating. Setting
`similarity_top_k=1` for the single-document questions shows retrieval
actually distinguishing between the two documents; `similarity_top_k=2`
for the cross-document question shows both being retrieved and combined
on purpose. At real-world scale (many Nodes per document), the default
`top_k=2` wouldn't have this problem, this lesson's `data/` is just small
enough that it needs calling out explicitly.

## The code, piece by piece

```python
documents = SimpleDirectoryReader(str(DATA_DIR)).load_data()
index = VectorStoreIndex.from_documents(documents)
```

Both files load into one list of `Document`s and build one index, exactly
the same call as every earlier lesson, just pointed at two unrelated
files instead of three related ones.

```python
narrow_query_engine = index.as_query_engine(similarity_top_k=1)
```

Retrieves only the single most relevant Node per question, at this
fixture's scale this means "only the one document that's actually
relevant."

```python
sources = sorted({Path(n.metadata["file_name"]).name for n in response.source_nodes})
```

A set comprehension over `response.source_nodes`, deduplicated and
sorted, printed alongside every answer to show exactly which file(s)
backed it.

```python
combined_query_engine = index.as_query_engine(similarity_top_k=2)
```

For the one question whose full answer needs a fact from each document
(the robot's own safe-hold timeout from the FAQ, plus the on-call
acknowledgment window from the handbook), `similarity_top_k=2` retrieves
one Node from each document, and the LLM synthesizes across both.

## Running it

```bash
uv run python lessons/llamaindex/02_intermediate/13_multi_document_indexes/lesson.py
```

## Expected output

Answer wording varies between runs (this is paraphrase, not verbatim
source text), sources and node counts are stable. Real captured run:

```
Loaded 2 documents: ['engineering_handbook.txt', 'product_faq.txt']
Index built. Nodes stored: 2

Q: How many approvals does a pull request need?
A: A pull request needs at least one approval before merging, and two approvals for changes that touch the robot's motion-control firmware.
   (sources: ['engineering_handbook.txt'])

Q: How long does the Cobalt-1's battery last?
A: A fully charged Cobalt-1 battery lasts for approximately 8 hours of continuous picking work.
   (sources: ['product_faq.txt'])

Q: If a Cobalt-1 loses connectivity and pages the on-call engineer, how long can it be before someone has to act, combining both the robot's own safe-hold timeout and the on-call acknowledgment window?
A: When the Cobalt-1 loses connectivity, it enters a safe-hold state after more than 10 seconds. If this triggers a page to the on-call engineer, the required acknowledgment time depends on the time of day:

* **During business hours:** Within 15 minutes of being paged.
* **Overnight:** Within 30 minutes of being paged.

Combining the initial 10-second loss of connectivity with the acknowledgment window means an engineer must act within roughly 15 minutes and 10 seconds during business hours, or 30 minutes and 10 seconds overnight.
   (sources: ['engineering_handbook.txt', 'product_faq.txt'])
```

Note the first two questions each retrieved sources from exactly one
file, matched to the question's actual topic, and the last question
pulled from both.

## Checkpoint

- One `VectorStoreIndex` can span any number of unrelated documents,
  nothing about `from_documents()` requires the documents to be topically
  related.
- `response.source_nodes[i].metadata["file_name"]` is how you attribute
  an answer back to its source document(s), whether one document or
  several backed it.
- `similarity_top_k` controls how many Nodes retrieval pulls back, at
  small scale (few Nodes per document) it can determine whether
  retrieval reads as "found the one relevant document" or "returned
  everything regardless of relevance."
- A question phrased to need facts from multiple documents forces a
  query engine to retrieve from, and synthesize across, more than one
  source, visible directly in `source_nodes`.

If anything here still feels unclear, ask before moving to Lesson 14.
