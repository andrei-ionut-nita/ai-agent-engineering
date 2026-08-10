# Lesson 1: What is LlamaIndex?

## The other major RAG/agent framework

This repo's `lessons/langchain` course already taught you the biggest
name in this space. LlamaIndex is the other one, and it's worth
learning on its own terms rather than as "LangChain but different,"
because it starts from a genuinely different center of gravity.

LangChain is **chain-centric**: its core abstraction is a `Runnable`,
a step you can compose with other steps into arbitrary pipelines. RAG
(retrieval-augmented generation, searching your own documents before
asking the model to answer) is one thing you can build with LangChain,
alongside agents, simple prompt chains, tool-calling loops, and more.

LlamaIndex is **data-centric**: its core abstraction is an `Index`, and
the framework's whole shape is built around one path: ingest documents,
build an index, query it. RAG isn't a feature you opt into, it's the
default thing the framework does. Agents and tool-calling exist in
LlamaIndex too (Lessons 14-17 of this course), but they're built as a
layer on top of that indexing core, not the other way around.

| | LangChain | LlamaIndex |
|---|---|---|
| Core abstraction | `Runnable` (a composable step) | `Index` (searchable data) |
| Default use case | Whatever you compose | RAG over your documents |
| Config style | Pass objects explicitly to each call | A global `Settings` object (Lesson 3) |
| Vocabulary | `Document`, `TextSplitter`, `VectorStore` | `Document`, `Node`, `Index` |
| Agents | `create_agent` + tools | `FunctionAgent` + `QueryEngineTool` |

## When to reach for which

Neither is strictly better. If you're building something where
retrieval is one step among several arbitrary ones (call a tool, then
a model, then another tool, maybe loop), LangChain's composability is
a more natural fit, especially paired with LangGraph. If the heart of
what you're building really is "let an LLM answer questions about a
pile of documents," LlamaIndex gets you there in fewer lines, with more
of the RAG-specific machinery (chunking strategies, retrieval modes,
response synthesis modes) built in and named for exactly that job.

In production, they're not even mutually exclusive: Lesson 23 of this
course shows wrapping a LlamaIndex query engine as a tool inside a
LangGraph or Pydantic AI agent, using each framework for what it's
best at.

## This course's prerequisite

This course assumes you've done `lessons/langchain` at least through
its RAG lessons (27-29), so it moves faster through ideas you've
already seen (what an embedding is, why chunking matters, what
similarity search does) and spends its explanations on what's actually
new here: LlamaIndex's own vocabulary, `Document`, `Node`, `Index`.

## Setup

None beyond what you already have. This course reuses the same
`GOOGLE_API_KEY` from your `.env` file and the same `uv sync`-installed
`.venv` as every other course in this repo, `llama-index`,
`llama-index-llms-google-genai`, and `llama-index-embeddings-google-genai`
are already in `pyproject.toml`.

## The code, piece by piece

```python
LANGCHAIN_VS_LLAMAINDEX = { ... }
```

A plain Python dict used purely to print a comparison table, no
LlamaIndex import yet. `dict.items()` is used to loop over both the key
(aspect) and value (comparison) together.

```python
print("This course's core loop, spelled out ...")
```

Names the four objects this course builds up over Lessons 2-5:
`Document` (raw source text), `Node` (a chunk of a Document, the unit
actually stored and searched), `Index` (Nodes plus their embeddings),
and `QueryEngine` (wraps an Index to answer questions).

## Running it

```bash
uv run python lessons/llamaindex/01_beginner/01_what_is_llamaindex/lesson.py
```

## Expected output

No network calls, so this is exact:

```
LangChain (lessons/langchain) vs LlamaIndex (this course):

  Core mental model:
    compose arbitrary steps (chains/graphs) vs ingest -> index -> query

  RAG's role:
    one feature among many vs the default, central use case

  Main building block:
    Runnable / chain vs Document -> Node -> Index

  Config style:
    pass objects explicitly through each call vs a global Settings object

  Agents:
    create_agent, tool-calling loops vs FunctionAgent over QueryEngineTools

  Where it shines:
    arbitrary multi-step orchestration vs fast, opinionated RAG over documents

This course's core loop, spelled out (Lessons 2-5 build this for real):
  1. Document   -- your raw source text, e.g. a .txt file
  2. Node       -- a chunk of a Document, the unit the index actually stores
  3. Index      -- Nodes plus their embeddings, organized for search
  4. QueryEngine -- wraps an Index: retrieve relevant Nodes, then ask the LLM
                     to synthesize an answer from them

No new setup needed: this course reuses the same GOOGLE_API_KEY and the same uv-managed .venv as every other course in this repo.
```

## Checkpoint

- **LangChain is chain-centric**, composing arbitrary steps; **LlamaIndex
  is data-centric**, built around ingest -> index -> query.
- RAG is a feature in LangChain, but the default path in LlamaIndex.
- The four core objects you'll build for real starting next lesson:
  `Document`, `Node`, `Index`, `QueryEngine`.
- This course assumes `lessons/langchain` through Lesson 29 is already
  done, so it won't re-explain embeddings or chunking from zero.
- No new setup: same `GOOGLE_API_KEY`, same `.venv`.

If anything here still feels unclear, ask before moving to Lesson 2.
