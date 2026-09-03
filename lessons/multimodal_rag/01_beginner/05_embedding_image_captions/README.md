# Lesson 5: Embedding Image Captions

## Where we left off

Lesson 4 turned an image into a caption, plain text. This lesson does
nothing new conceptually, it hands that caption to the exact same
embedding call `naive_rag` Lesson 2 used for a text chunk. That's the
entire payoff of choosing captioning-then-embed back in Lesson 1: once
an image becomes a caption, it is, as far as embedding is concerned,
indistinguishable from any other piece of text in this series.

## The code, piece by piece

```python
caption = caption_image(IMAGE_PATH)
vector = embed_texts([caption])[0]
```

`embed_texts` here is `naive_rag` Lesson 2's `embed_content` call,
copied verbatim, same model (`models/gemini-embedding-001`), same
`output_dimensionality` (768). No parameter changes, no "image mode",
because by the time this function runs, there is no image left, only
the caption string `caption_image` produced.

```python
print(f"Vector length: {len(vector)}")
```

768 numbers, exactly the same shape a text chunk's embedding has. This
is worth confirming directly rather than taking on faith: it's what
makes Lesson 6's mixed store possible, a text chunk's vector and an
image caption's vector can sit in the same list and be compared with
the same cosine similarity function, because nothing about their shape
tells them apart.

## Running it

```bash
uv run python lessons/multimodal_rag/01_beginner/05_embedding_image_captions/lesson.py
```

## Expected output

```
Caption:
<detailed description of the derailleur hanger diagram>

Vector length: 768
First 5 numbers: [...]
```

## Checkpoint

- Once an image is captioned, its embedding uses the identical call,
  model, and dimensionality as any text chunk in this series.
- A caption's vector and a text chunk's vector are the same shape,
  there is nothing in the vector itself that marks it as "came from an
  image." Lesson 11 adds that information back as metadata, on
  purpose, once it turns out to matter for citing sources correctly.

If anything here still feels unclear, ask before moving to Lesson 6.
