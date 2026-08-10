# Lesson 11: Metadata filtering

## Searching a subset of the index

Every retrieval so far has searched the whole index: every stored Node is
a candidate, similarity search ranks all of them, and the top matches win.
`MetadataFilters` narrows that search space before ranking even happens,
restricting retrieval to only the Nodes whose metadata satisfies a
condition, e.g. only Nodes from one specific source file.

This matters once an index holds more than a handful of documents. If you
already know a question belongs to one document (a user picked a file in
a UI, or a router step upstream already decided "this is a vacation
question"), searching the entire index anyway wastes both similarity
search accuracy (results from irrelevant documents can outscore the right
document's less-central chunks) and, at scale, latency.

| | Unfiltered retrieval | `MetadataFilters` retrieval |
|---|---|---|
| Candidate Nodes | Every Node in the index | Only Nodes matching the filter |
| When applied | N/A | Before similarity ranking, not after |
| Good for | "Search everything I have" | "Search only this document / category" |
| LangChain equivalent | `retriever.invoke(query)` | `vectorstore.as_retriever(search_kwargs={"filter": ...})` |

## The pieces

- **`MetadataFilters`** (`llama_index.core.vector_stores`): a container
  for one or more filter conditions, combined with AND/OR.
- **`ExactMatchFilter`**: an alias for `MetadataFilter` using the default
  `FilterOperator.EQ`, checks a metadata key equals a given value exactly.
  Every Node's metadata already carries `file_name` (Lesson 2), which is
  what this lesson filters on.
- Filters attach to either `index.as_retriever(filters=...)` (raw
  retrieval, no LLM call) or `index.as_query_engine(filters=...)` (Lesson
  5's full retrieve-then-synthesize pipeline).

## The code, piece by piece

```python
vacation_filter = MetadataFilters(
    filters=[ExactMatchFilter(key="file_name", value="vacation_policy.txt")]
)
```

One condition: `node.metadata["file_name"] == "vacation_policy.txt"`.
`MetadataFilters` takes a list so multiple conditions can be combined
(default: AND).

```python
filtered_retriever = index.as_retriever(similarity_top_k=3, filters=vacation_filter)
filtered_nodes = filtered_retriever.retrieve(question)
```

The filter is applied before the top-k similarity search runs, not
afterward, so it's not "search everything, then throw away the
mismatches," it's "only ever consider these Nodes in the first place."

```python
filtered_query_engine = index.as_query_engine(filters=vacation_filter)
response = filtered_query_engine.query(question)
sources = sorted({Path(n.metadata["file_name"]).name for n in response.source_nodes})
```

Same `filters=` keyword works on a query engine. `response.source_nodes`
lists every Node the LLM actually used to synthesize its answer, checking
their `file_name` metadata is how you confirm the filter did what you
expect: every source should be `vacation_policy.txt`, nothing else.

## Running it

```bash
uv run python lessons/llamaindex/02_intermediate/11_metadata_and_filtering/lesson.py
```

## Expected output

Similarity scores are stable to several decimal places for a fixed query
against a fixed embedding model, but can drift slightly between API
calls, treat the digits after the first two decimal places as
approximate. The LLM's final answer wording may vary slightly, this is
one real captured run:

```
Index built over 3 documents: ['expense_policy.txt', 'remote_work_policy.txt', 'vacation_policy.txt']

--- Unfiltered retrieval for: 'How many days of leave does an employee get per year?' ---
  score=0.6967  source=vacation_policy.txt
  score=0.6366  source=remote_work_policy.txt
  score=0.5901  source=expense_policy.txt

--- Filtered retrieval (file_name == 'vacation_policy.txt') ---
  score=0.6967  source=vacation_policy.txt

Filtered query engine answer:
  Full-time employees accrue 20 days of paid vacation per calendar year. Additionally, the company offers 10 paid public holidays per year and 12 weeks of paid parental leave for a new child.
  (sources used: ['vacation_policy.txt'])
```

Notice the unfiltered search returns all three files (this fixture index
only has one Node per file, so "top 3" is "all of them" here), while the
filtered search returns only `vacation_policy.txt`, at exactly the same
score it got unfiltered, confirming the filter narrows candidates without
changing how they're scored.

## Checkpoint

- **`MetadataFilters`**: restricts which Nodes a retriever or query
  engine can even consider, applied before similarity ranking.
- **`ExactMatchFilter`**: the common case, `metadata[key] == value`, an
  alias for `MetadataFilter` with `FilterOperator.EQ`.
- Attach filters via `index.as_retriever(filters=...)` or
  `index.as_query_engine(filters=...)`.
- `response.source_nodes[i].metadata["file_name"]` is how you verify
  which document(s) actually backed an answer, filtered or not.
- Filtering is most useful once you have more documents than you want to
  search on every query, e.g. after a routing step already narrowed down
  which document a question belongs to.

If anything here still feels unclear, ask before moving to Lesson 12.
