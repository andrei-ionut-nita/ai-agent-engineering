# Lesson 8: Embeddings with Ollama

## A different kind of model

Every lesson so far used `llama3.2`, a **generation** model: text in,
new text out. `nomic-embed-text` is a different kind of model
entirely, an **embedding** model, it can't chat or answer questions at
all. Its only job is to turn text into a fixed-length list of numbers
(a vector) that captures the text's meaning, the same concept the
langchain course covers in its final RAG lessons and pgvector builds
an entire course around, just running on your own machine here
instead of calling out to Google.

Setup: pull the embedding model first (small, under 300 MB):

```bash
ollama pull nomic-embed-text
```

## The code, piece by piece

```python
response = ollama.embed(model="nomic-embed-text", input=SENTENCES)
```

`embed()` takes a list of strings and returns one vector per string,
in the same order you passed them in. Passing a list instead of
calling `embed()` once per sentence lets Ollama batch the work
internally, which matters once you're embedding hundreds of chunks
for a real RAG pipeline (Lesson 21 builds exactly that).

```python
def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot_product / (norm_a * norm_b)
```

Cosine similarity measures the angle between two vectors, ignoring
their length: `1.0` means they point in exactly the same direction
(as similar in meaning as this model can represent), `0.0` means
they're unrelated. This is hand-rolled here with plain Python so the
math is visible; the pgvector course uses Postgres's `<=>` operator to
do the same computation directly in the database instead.

```python
cosine_similarity(dog_vec, puppy_vec)
cosine_similarity(dog_vec, tax_vec)
```

Two sentences about pets should score meaningfully higher than a pet
sentence compared against a sentence about taxes, even though none of
the words overlap between "dog" and "puppy" beyond the general topic.
That's the entire point of an embedding: it captures meaning, not
just shared words.

## Running it

```bash
uv run python lessons/ollama/01_beginner/08_embeddings_with_ollama/lesson.py
```

## Expected output

```
Got 3 embeddings, each 768 numbers long.

'a happy dog' vs 'a joyful puppy': 0.866
'a happy dog' vs 'quarterly tax filing': 0.336
```

The exact numbers may shift slightly between Ollama versions, but the
pattern should hold clearly: the dog/puppy pair well above 0.7, the
dog/tax pair well below it.

## Checkpoint

- **Embedding model**: a model that turns text into a vector, cannot
  chat or generate text, a different job than `llama3.2`.
- **`ollama.embed()`**: takes a list of strings, returns one vector per
  string, batched.
- **Cosine similarity**: measures how closely two vectors point in the
  same direction, the standard way to compare embeddings.
- **Why this matters**: this is the mechanism behind semantic search
  and RAG, whether running locally here or in Postgres in the pgvector
  course.

If anything here still feels unclear, ask before moving to Lesson 9,
this course's beginner checkpoint project.
