# Lesson 1: What Is Hybrid RAG?

## Where we left off

If you've done [`naive_rag`](../../../naive_rag/), you already know dense
retrieval: embed a query, embed every chunk, rank by cosine similarity,
take the top `k`. It works because embeddings capture *meaning*, so a
question and its answer end up close together in vector space even when
they don't share a single word.

That strength is also dense retrieval's weakness. Meaning is exactly what
an embedding model is good at, and exactly what a firmware build number,
a part number, or a product SKU doesn't have much of. A string like
`20240115` or `E3D-CHT-04` means almost nothing on its own, an embedding
model has no real signal to place it precisely, it just gets folded into
"whatever the surrounding paragraph is about."

## The specific gap

**Hybrid RAG** combines dense retrieval (good at meaning, paraphrase,
synonyms) with **sparse retrieval** (good at exact token overlap: IDs,
model numbers, acronyms, rare proper nouns), and fuses the two rankings
into one. Neither retriever is replaced, both run, and their results are
combined so a question can be answered by whichever one actually has the
signal for it.

## The code, piece by piece

```python
QUESTION = "What is firmware build 20240115 for?"
```

This question is built entirely around one exact, rare token. The
correct document does contain that exact string, but buried in a
paragraph about video calls and brick walls, nothing about the sentence
around it screams "firmware."

```python
scored = [
    (path.name, cosine_similarity(query_vector, vector))
    for path, vector in zip(paths, doc_vectors)
]
```

Same dense retrieval as `naive_rag`, nothing new here, six documents,
one query, ranked by cosine similarity. The point of this lesson isn't
the code, it's what the ranking looks like once it runs.

## Running it

```bash
uv run python lessons/hybrid_rag/01_beginner/01_what_is_hybrid_rag/lesson.py
```

## Expected output

Scores vary slightly between runs (the embedding model isn't perfectly
deterministic), but the shape holds:

```
Question: 'What is firmware build 20240115 for?'

Dense retrieval ranking (cosine similarity, highest first):
  0.6475  home_network.md <- contains the exact string 'firmware build 20240115'
  0.5884  old_travel_router.md
  0.5135  3d_printer.md
  0.4947  bike_maintenance.md
  0.4674  espresso_machine.md
  0.4584  houseplants.md

Dense retrieval got the right document this time, but only by 0.0592, a
thin margin for a question that has exactly one correct answer...
```

Notice the runner-up: `old_travel_router.md`, another note about a
router's firmware, just a different router with a different build
number. The right document usually still wins, but by a thin margin
against a document that's topically almost identical, differing only in
the one exact detail the question actually asked about. Dense retrieval
knows "this is about router firmware," it just can't reliably tell
*which* router firmware, because a build number carries almost no
meaning of its own. Run it a few times, and watch that margin occasionally
flip.

## Checkpoint

- **Dense retrieval's blind spot**: exact IDs, model numbers, acronyms,
  and rare proper nouns carry almost no "meaning" for an embedding model
  to place precisely, so dense retrieval finds them by accident, if at
  all, not reliably.
- **Sparse retrieval** (built starting Lesson 3) is the fix for exactly
  this case, exact token overlap, no notion of meaning required.
- **Hybrid RAG**: run both, fuse the rankings, so meaning-based and
  token-based retrieval each cover the other's blind spot.

If anything here still feels unclear, ask before moving to Lesson 2.
