# Lesson 14: When Sparse Wins

## Where we left off

Lesson 6 showed sparse retrieval winning on bare IDs and losing on pure
paraphrase. This lesson turns that observation into something usable
before a query is even run: a rule of thumb for predicting, in advance,
which retriever a given question is likely to need.

## The code, piece by piece

```python
ID_SHAPED = re.compile(r"[0-9]|-|^[A-Z]{2,}$")

def has_id_shaped_token(query: str) -> bool:
    return any(ID_SHAPED.search(token) for token in query.split())
```

A crude signal: does any word in the query contain a digit, a hyphen, or
look like an all-caps acronym? None of those carry much "meaning" for an
embedding model to place precisely (Lesson 1's whole premise), so a
query built around one is a query where sparse retrieval's literal
matching has the advantage.

## Running it

```bash
uv run python lessons/hybrid_rag/02_intermediate/14_where_sparse_wins/lesson.py
```

## Expected output

```
query                                                   predict
20240115                                                sparse
E3D-CHT-04                                              sparse
Puly Caff Plus                                          dense
8 Nm                                                    sparse
FoliGrow 9-3-6                                          sparse
Why does my espresso taste weak and sour lately?        dense
Why does my bike skip gears when climbing hills?        dense
```

Four of five lexical queries from Lesson 6 get flagged correctly. The
fifth, `"Puly Caff Plus"`, doesn't, no digit, no hyphen, no all-caps run,
just a proper noun the heuristic's regex has no rule for, even though
it's exactly the kind of rare, exact-match token sparse retrieval is
good at. That's the honest limit of a heuristic built on surface
punctuation: it catches the *shape* of an ID, not the underlying reason
IDs and rare proper nouns both trip up dense retrieval, that they're
uncommon enough in the embedding model's training data to not carry
reliable meaning. A better (and more expensive) version of this
heuristic would check corpus term frequency directly, rather than
guessing from punctuation.

## Checkpoint

- **The heuristic**: a query token with a digit, hyphen, or all-caps
  acronym shape is a signal sparse retrieval likely has the advantage.
- **Its blind spot**: rare proper nouns with no digits or punctuation
  (a product name, a person's name) trip up dense retrieval the same
  way, without matching this particular rule.
- Heuristics like this are useful for deciding *which retriever's result
  to trust more*, not a replacement for running both and fusing, which
  is why this course fuses by default rather than routing.

If anything here still feels unclear, ask before moving to Lesson 15.
