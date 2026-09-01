# Lesson 3: Cosine Similarity by Hand

## What we're building

A function that takes two embeddings from Lesson 2 and returns one
number: how similar their meanings are. No library does this for us
here, it's about fifteen lines of ordinary math, so there's no mystery
left in what "similarity search" actually means.

## What "similar" means as a number

Picture each 768-number vector as an arrow pointing from the origin out
into a 768-dimensional space (impossible to draw, but the 2D and 3D
intuition still holds). Two vectors representing similar meanings tend
to point in roughly the same direction, even if one is longer than the
other. **Cosine similarity** measures exactly that: the angle between
two vectors, ignoring their length entirely.

The result is always between -1 and 1:
- **1** means the two vectors point in exactly the same direction (as
  similar as it gets).
- **0** means they're at a right angle (unrelated).
- **-1** means they point in opposite directions (opposite meaning),
  rare in practice for embeddings of ordinary text.

## The code, piece by piece

```python
dot_product = sum(x * y for x, y in zip(a, b))
```

The **dot product**: pair up each vector's numbers by position (`zip`),
multiply each pair, and add up all 768 results into one number. Two
vectors pointing the same way produce a large dot product; pointing in
unrelated directions, matching positions are as likely to have opposite
signs as the same sign, so the products partly cancel out and the sum
stays small.

```python
magnitude_a = math.sqrt(sum(x * x for x in a))
```

A vector's **magnitude** is its own length, computed the same way you'd
find the length of a 2D arrow with the Pythagorean theorem
(`sqrt(x² + y²)`), just extended to all 768 numbers instead of 2. This
matters because a longer vector produces a bigger dot product purely
from being longer, not from being more similar, we need to divide that
effect back out.

```python
return dot_product / (magnitude_a * magnitude_b)
```

Dividing the dot product by both magnitudes cancels out each vector's
own length, leaving a number that depends only on the *angle* between
them, exactly the cosine of that angle, which is where the name comes
from.

## Running it

```bash
uv run python lessons/naive_rag/01_beginner/03_cosine_similarity_by_hand/lesson.py
```

## Expected output

```
Query:     'How do I keep my tomatoes healthy?'
Related:   'The tomato bed is watered daily and grows basil alongside it.'
Unrelated: 'Practice sessions are thirty minutes a day, five days a week.'

Similarity to related text:   0.6885
Similarity to unrelated text: 0.5051
```

The exact numbers will differ slightly between runs, but the related
text's score should consistently beat the unrelated text's, even though
neither sentence shares a single word with the query ("tomatoes",
"healthy") beyond "tomato." That gap, however small it looks printed as
raw numbers, is the entire signal Naive RAG's retrieval step relies on.

If you see two very close, hard-to-distinguish numbers instead of a
clear gap, that's still expected occasionally, cosine similarity between
embeddings of ordinary sentences (even unrelated ones) tends to sit in a
fairly narrow, model-dependent band rather than spanning the full -1 to
1 range; what matters is the relative ordering, not the absolute value.

## Checkpoint

- **cosine similarity**: the cosine of the angle between two vectors, a
  number from -1 to 1, where higher means more similar in meaning.
- **dot product**: multiply matching positions, sum the results, the raw
  ingredient similarity is built from.
- **magnitude**: a vector's own length; dividing by both vectors'
  magnitudes removes the effect of length, leaving only direction.
- This is the exact function Naive RAG uses to decide which chunks of a
  document are relevant to a question.

If anything here still feels unclear, ask before moving to Lesson 4.
