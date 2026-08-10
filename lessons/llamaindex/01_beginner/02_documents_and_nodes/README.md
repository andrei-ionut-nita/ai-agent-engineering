# Lesson 2: Documents and Nodes

## The fixture data

This lesson adds a `data/` folder with three short `.txt` files: a
fictional company's ("Nimbus Robotics") vacation, remote work, and
expense policies. These same three files get reused, unchanged, by
most of the rest of this course's beginner tier, the same pattern
`lessons/langchain/03_advanced/27_document_loading_and_splitting/data/notes.txt`
uses for its own RAG lessons.

## Document: your raw source text

A `Document` is LlamaIndex's wrapper around one whole source file: its
raw text (`.text`) plus metadata about where it came from
(`.metadata`), conceptually identical to LangChain's
`Document(page_content=..., metadata=...)`. `SimpleDirectoryReader` is
the most common way to produce them: point it at a folder, and it
reads every file inside, one `Document` per file, auto-detecting type
(`.txt`, `.pdf`, `.md`, `.docx`, and more).

## Node: the unit an index actually stores

A `Document` is usually too big to hand an index as one unit, so it
gets split into `Node` objects. A `Node` is a chunk of a `Document`,
and it's the thing an `Index` actually stores, embeds, and retrieves,
not the whole `Document`. Each `Node` carries three things:

- **Text**: the chunk's own slice of the original document.
- **Metadata**: inherited from the parent `Document` (file name, file
  path, and more), so a retrieved `Node` always tells you where it
  came from.
- **Relationships**: links to neighboring `Node`s, e.g. which came
  right before or after it in the source `Document`. An index can use
  this later to pull in surrounding context around a match, not just
  the matched chunk in isolation.

| | Document | Node |
|---|---|---|
| Represents | One whole source file | One chunk of that file |
| Produced by | `SimpleDirectoryReader` | A node parser (e.g. `SentenceSplitter`) |
| Stored/embedded by an Index? | No | Yes |
| Carries relationships to neighbors? | No | Yes |

`SentenceSplitter` is the node parser this lesson uses, LlamaIndex's
rough equivalent of LangChain's `RecursiveCharacterTextSplitter`: it
tries to break text on sentence boundaries rather than mid-sentence,
given a target `chunk_size` (measured in tokens, not characters) and a
`chunk_overlap`.

## The code, piece by piece

```python
documents = SimpleDirectoryReader(str(DATA_DIR)).load_data()
```

Reads every file in `data/` and returns a list of `Document` objects,
one per file.

```python
splitter = SentenceSplitter(chunk_size=200, chunk_overlap=20)
nodes = splitter.get_nodes_from_documents(documents)
```

Splits every `Document` into `Node`s. `chunk_size=200` is measured in
*tokens*, which is why the printed chunks below run to 400-650
characters, not 200, tokens are roughly 3-4 characters each for
English text. `chunk_overlap=20` repeats the last 20 tokens of one
chunk at the start of the next, so a sentence that would otherwise be
cut in half at a chunk boundary still has full context in at least one
of the two chunks.

```python
print(f"  node_id: {first_node.node_id[:8]}...")
print(f"  metadata keys: {sorted(first_node.metadata.keys())}")
print(f"  relationships: {sorted(r.name for r in first_node.relationships)}")
```

Every `Node` has a unique `node_id`. Its `metadata` dict is inherited
from the parent `Document` plus a few fields `SimpleDirectoryReader`
adds automatically (file name, size, timestamps). Its `relationships`
dict maps relationship kinds (`SOURCE`, the parent `Document`; `NEXT`
and `PREVIOUS`, sibling `Node`s) to references.

## Running it

```bash
uv run python lessons/llamaindex/01_beginner/02_documents_and_nodes/lesson.py
```

## Expected output

No LLM or embedding calls here, this is exact except for the
`node_id`, which is a random UUID prefix each run:

```
Loaded 3 documents from data/:

  expense_policy.txt: 1045 characters
  remote_work_policy.txt: 1056 characters
  vacation_policy.txt: 978 characters

Split into 6 nodes:

--- Node 0 (from expense_policy.txt, 609 chars) ---
Nimbus Robotics: Expense Reimbursement Policy
...

--- Node 5 (from vacation_policy.txt, 347 chars) ---
New hires begin accruing vacation from their first day, but cannot use
more than 5 days during their first 90 days of employment, matching the
standard onboarding probation period.

Nimbus Robotics also observes 10 paid public holidays per year, and
offers 12 weeks of paid parental leave for a new child, whether by
birth, adoption, or fostering.

First node's attributes:
  node_id: dda78d0d...
  metadata keys: ['creation_date', 'file_name', 'file_path', 'file_size', 'file_type', 'last_modified_date']
  relationships: ['NEXT', 'SOURCE']
```

(Full Node text for all 6 nodes is printed when you actually run it,
trimmed here for length.)

## Checkpoint

- **Document**: a whole source file's raw text plus metadata,
  typically produced by `SimpleDirectoryReader`.
- **Node**: a chunk of a Document, the actual unit an Index stores,
  embeds, and retrieves. Carries text, inherited metadata, and
  relationships to neighboring Nodes.
- **`SentenceSplitter`**: LlamaIndex's node parser, sentence-aware
  chunking with a `chunk_size` measured in tokens and a
  `chunk_overlap`, the rough equivalent of LangChain's
  `RecursiveCharacterTextSplitter`.
- Splitting into Nodes is pure local computation, no LLM or embedding
  calls needed, those come in Lesson 4 when an Index is actually built.

If anything here still feels unclear, ask before moving to Lesson 3.
