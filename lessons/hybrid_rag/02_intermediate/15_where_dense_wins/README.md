# Lesson 15: When Dense Wins

## Where we left off

Lesson 14 built a diagnostic for spotting a sparse-favoring query in
advance. This lesson builds the mirror: a diagnostic for spotting a
dense-favoring one, by directly measuring how much vocabulary a query
actually shares with its own correct answer.

## The code, piece by piece

```python
STOPWORDS = {"a", "an", "and", ..., "why", ...}

def tokenize(text: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return {token for token in tokens if token not in STOPWORDS}
```

Function words ("why," "does," "my") show up in nearly every document
regardless of topic. Counting them as "shared vocabulary" would be
Lesson 3's raw-term-frequency mistake all over again, common words
looking like a signal when they're really just noise every document has
anyway.

```python
def overlap_ratio(query, document_text) -> float:
    shared = tokenize(query) & tokenize(document_text)
    return len(shared) / len(tokenize(query))
```

What fraction of the query's *content* tokens appear literally anywhere
in the document that actually answers it? High overlap: sparse
retrieval has real tokens to latch onto. Low overlap: it doesn't, and
dense retrieval has to carry the question on meaning alone.

## Running it

```bash
uv run python lessons/hybrid_rag/02_intermediate/15_where_dense_wins/lesson.py
```

## Expected output

```
query                                                             overlap  predict
20240115                                                              1.00 sparse
E3D-CHT-04                                                            1.00 sparse
Puly Caff Plus                                                        1.00 sparse
FoliGrow 9-3-6                                                        1.00 sparse
8 Nm                                                                  1.00 sparse
Why does my video call in the back bedroom keep freezing?             0.50 dense
Why do vertical walls have ridges even though I didn't change any settings?     0.50 dense
Why is my espresso tasting sour and weak lately?                      0.40 dense
Why does my fig tree keep losing leaves from the bottom?              0.50 dense
Why does my bike skip gears when climbing hills?                      0.40 dense
```

The five lexical queries score a perfect `1.00`, every content token
they contain is, definitionally, the exact token the document contains.
The paraphrased queries land around `0.40`-`0.50`, not zero, a couple of
ordinary setting words (`"back bedroom"`) leak through by coincidence,
but well below the lexical queries, and specifically missing the words
doing the real explanatory work: `"firmware,"` `"nozzle,"` `"scale,"`
`"nitrogen,"` `"derailleur"` never appear in any paraphrased query at
all. That gap between "some incidental overlap" and "the load-bearing
vocabulary is entirely absent" is the real signal, not a literal zero.

## Checkpoint

- **Overlap ratio**: the fraction of a query's content tokens (stopwords
  excluded) that appear in its correct answer, computed directly rather
  than guessed at from punctuation the way Lesson 14's heuristic did.
- A high ratio predicts sparse retrieval has real signal; a low one
  (rarely a literal zero) predicts dense retrieval has to carry it,
  specifically because the *technical* vocabulary is missing, not
  because every single word is.
- Together, Lessons 14 and 15 give two independent, cheap-to-compute
  signals for which retriever a query is likely to need, useful for
  intuition, not a replacement for running and fusing both.

If anything here still feels unclear, ask before moving to Lesson 16.
