# Lesson 4: TF-IDF by Hand

## Where we left off

Lesson 3's flaw: raw term frequency treats every word equally, so a
question built out of common words ("what," "do," "it," "about") barely
discriminates between documents at all, whichever document is longest or
uses those common words most often tends to win, regardless of
relevance. **TF-IDF** fixes exactly this, by weighting each word's
contribution by how rare it is across the whole corpus.

## The code, piece by piece

```python
def inverse_document_frequency(term, documents) -> float:
    doc_count = sum(1 for doc in documents if term in doc)
    return math.log(len(documents) / doc_count)
```

For each term, count how many of the documents contain it at least
once. A term that shows up in every document tells you nothing about
which one is relevant, `log(6 / 6) = 0`, it contributes nothing to any
score. A term in just one document out of six is a real signal,
`log(6 / 1) ≈ 1.79`, and gets weighted up accordingly. The log keeps
this from scaling linearly, going from "rare" to "extremely rare" still
matters, just with diminishing returns.

```python
score += term_frequency * idf
```

Lesson 3's raw count, now multiplied by that rarity weight before being
added up. A word that appears often in this document *and* rarely
across the corpus drives the score the most, exactly the combination
that flags "this document is specifically about that."

## Running it

```bash
uv run python lessons/hybrid_rag/01_beginner/04_tfidf_by_hand/lesson.py
```

## Expected output

```
Query: 'Why does it happen and what should I do about it?'
(Lesson 3's raw term frequency gave: bike_maintenance.md, home_network.md, houseplants.md, 3d_printer.md, espresso_machine.md, barely separated)

   3.296  home_network.md
   2.603  3d_printer.md
   1.099  bike_maintenance.md
   0.405  houseplants.md
   0.405  old_travel_router.md
   0.000  espresso_machine.md

Query: 'What is firmware build 20240115 for?'
   8.160  home_network.md
   6.145  old_travel_router.md
   1.569  espresso_machine.md
   1.281  3d_printer.md
   0.182  houseplants.md
   0.000  bike_maintenance.md
```

This first query is deliberately generic, built from common words, so
there's no single "correct" document to check against, the useful
comparison is against Lesson 3's own result, not a ground truth.
`bike_maintenance.md` went from Lesson 3's clear #1 (raw score 13) down
to #3 here, once the common words padding its score got downweighted,
and the gap between top and bottom widened into a document scoring
exactly zero, something raw term frequency never produced.

The firmware question is the more telling one: Lesson 3's 8-8 tie
between `home_network.md` and `old_travel_router.md` is gone,
`home_network.md` now wins decisively, 8.160 to 6.145. `20240115`
appears in exactly one of six documents, so its IDF weight is high,
while `firmware` and `build`, the words both documents share, get
downweighted toward zero. Rarity weighting breaks exactly the tie raw
counting couldn't.

## Checkpoint

- **TF-IDF**: term frequency, multiplied by inverse document frequency,
  downweighting words that appear everywhere, upweighting words that
  appear almost nowhere.
- **IDF**: `log(total documents / documents containing this term)` - a
  word in every document contributes zero; a word in one document out of
  many contributes a lot.
- This is still sparse retrieval, still zero embedding calls, just a
  smarter way to count.

If anything here still feels unclear, ask before moving to Lesson 5.
