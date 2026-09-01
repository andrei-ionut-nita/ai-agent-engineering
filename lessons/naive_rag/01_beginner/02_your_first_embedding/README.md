# Lesson 2: Your First Embedding

## What we're building

A tiny program that turns one sentence into a vector: a fixed-length
list of numbers, produced by an AI model trained specifically to make
"meaning" measurable. This is the "embed" stage of Naive RAG's four
stages, done in isolation before it's part of anything bigger.

## What an embedding actually is

Gemini's chat model, from Lesson 1, takes text in and produces text out.
An **embedding model** is different: it takes text in and produces a
list of floating-point numbers out, always the same length no matter how
long the input text was. That list is called a **vector**, and it's
positioned in a very high-dimensional space such that two pieces of text
with similar meaning end up with vectors that are close together in that
space, and two pieces of text with unrelated meaning end up far apart.

Nothing about a vector is human-readable on its own, printing one just
shows a list of numbers like `-0.0153, 0.0106, 0.0268, ...`. Its value
comes entirely from comparing it to other vectors, which Lesson 3 does
next.

## The code, piece by piece

```python
response = client.models.embed_content(
    model=EMBEDDING_MODEL,
    contents=[text],
    config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
)
```

`embed_content` is Gemini's embedding endpoint, the sibling of
`generate_content` from Lesson 1. `contents` takes a list, so you can
embed several pieces of text in one network call, this lesson passes
just one. `EmbedContentConfig(output_dimensionality=768)` asks Gemini to
return a 768-number vector specifically; left unset, this model's
vectors are 3072 numbers long. A smaller, fixed length keeps every
vector in this course comparable to each other and to this repo's
pgvector course, which uses the same 768 setting.

```python
values = response.embeddings[0].values
```

`response.embeddings` is a list (matching the list you passed in as
`contents`), so `[0]` is "the embedding for the first, and only, piece of
text we sent." `.values` is the actual list of floats.

## Running it

```bash
uv run python lessons/naive_rag/01_beginner/02_your_first_embedding/lesson.py
```

## Expected output

```
Text: "The garden's tomato bed is watered every day in summer."

Vector length: 768
First 5 numbers: [-0.0153, 0.0106, 0.0268, -0.0416, 0.0191]
Data type of each number: float
```

The exact numbers will differ slightly from this example (Gemini's model
version can change over time), but the length (768) and the shape (small
positive and negative decimals) will always look like this.

## Checkpoint

- **embedding**: a fixed-length list of numbers representing a piece of
  text's meaning, produced by an embedding model, not a chat model.
- **`embed_content`**: Gemini's embedding endpoint, siblings with
  `generate_content` from Lesson 1.
- **`output_dimensionality`**: fixes the vector's length, smaller values
  trade a little precision for smaller, faster-to-compare vectors.
- Two similar-meaning texts get similar vectors; this lesson only proves
  a vector exists, Lesson 3 proves the "similar" part.

If anything here still feels unclear, ask before moving to Lesson 3.
