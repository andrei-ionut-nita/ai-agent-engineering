# Lesson 3: Connecting Gemini, the Settings pattern

## A global object instead of explicit passing

Every LangChain lesson in this repo builds a model object and passes
it explicitly wherever it's needed: `ChatGoogleGenerativeAI(...)`, then
`model.invoke(...)`, or hands it into `create_agent(model=...)`.
LlamaIndex does this differently by default: it has one global object,
`Settings`, that most of the framework reads from automatically.

Set `Settings.llm` and `Settings.embed_model` once, and every `Index`,
`QueryEngine`, and `Agent` you build for the rest of a script picks
them up without you passing them in by hand each time. You can still
override per call when you need to (later lessons do), but the global
is the default, and it's the single biggest ergonomic difference
between how these two frameworks feel to write.

| | LangChain | LlamaIndex |
|---|---|---|
| Model setup | `model = ChatGoogleGenerativeAI(...)` | `Settings.llm = GoogleGenAI(...)` |
| Passed to each call? | Yes, explicitly | No, read from the global by default |
| Embeddings setup | `GoogleGenerativeAIEmbeddings(...)`, passed to a vector store | `Settings.embed_model = GoogleGenAIEmbedding(...)` |
| Override per call | Always explicit anyway | Possible, but the exception, not the rule |

## The code, piece by piece

```python
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
```

`GoogleGenAI` is LlamaIndex's LLM wrapper for Gemini, the equivalent of
LangChain's `ChatGoogleGenerativeAI`. `GoogleGenAIEmbedding` is the
embeddings equivalent of `GoogleGenerativeAIEmbeddings`.

```python
Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)
```

Same model names used throughout this repo: `gemini-3.5-flash-lite` for
the LLM, `models/gemini-embedding-001` for embeddings. Set once, at
module level or in `main()`, before building any Index.

```python
response = Settings.llm.complete("In one short sentence, what is a vector embedding?")
```

`.complete()` is a direct, index-free call to the LLM, proving the
connection works before Lesson 4 builds a real index on top of it.

```python
embedding = Settings.embed_model.get_text_embedding("hello world")
```

`.get_text_embedding()` turns one string directly into its vector, the
same operation an Index runs internally on every Node, exposed here so
you can see the shape of it: a list of floats, one number per
dimension.

## Running it

```bash
uv run python lessons/llamaindex/01_beginner/03_connecting_gemini/lesson.py
```

## Expected output

The direct LLM call's exact wording varies between runs, paraphrased
below; everything else is stable:

```
Settings configured:
  Settings.llm: GoogleGenAI (model=gemini-3.5-flash-lite)
  Settings.embed_model: GoogleGenAIEmbedding (model=models/gemini-embedding-001)

Direct LLM call:
  A vector embedding is a numeric representation of data (text, images,
  audio) that captures its meaning so similar items end up close together.

Direct embedding call:
  vector length: 3072
  first 5 values: [-0.03, 0.004, 0.0155, -0.0864, -0.0035]
```

## Checkpoint

- **`Settings`**: a global object holding the LLM and embedding model
  most of LlamaIndex reads from automatically, LlamaIndex's alternative
  to LangChain's pattern of passing model objects explicitly everywhere.
- Set `Settings.llm` and `Settings.embed_model` once, before building
  any `Index`.
- `GoogleGenAI` and `GoogleGenAIEmbedding` are LlamaIndex's wrappers for
  Gemini, matching the model names already used elsewhere in this repo.
- `.complete()` and `.get_text_embedding()` are direct, index-free calls
  useful for testing a connection or understanding what an Index does
  internally.

If anything here still feels unclear, ask before moving to Lesson 4.
