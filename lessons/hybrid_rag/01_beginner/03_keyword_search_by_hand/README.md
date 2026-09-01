# Lesson 3: Keyword Search by Hand

## Where we left off

Lesson 1 showed dense retrieval's blind spot: exact tokens like a
firmware build number carry almost no "meaning" for an embedding model
to place precisely. This lesson builds the other half of Hybrid RAG,
**sparse retrieval**, starting with the simplest possible version:
counting words.

Nothing here calls Gemini. Sparse retrieval doesn't need an embedding at
all, it works directly on the text.

## The code, piece by piece

```python
def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())
```

Lowercase everything, then split on anything that isn't a letter or
digit. `"20240115"` and a hyphenated part number both survive as clean
tokens, punctuation is what splits them apart, not the digits
themselves, this is exactly why sparse retrieval doesn't blur a rare ID
the way an embedding model does.

```python
def term_frequency_score(query_tokens, doc_tokens) -> int:
    return sum(doc_tokens.count(token) for token in query_tokens)
```

The entire algorithm: for every word in the query, count how many times
it shows up in this document, add it up. No weighting, no notion that
some words matter more than others, just raw counting. That simplicity
is both this lesson's point and its limitation, see below.

## Running it

```bash
uv run python lessons/hybrid_rag/01_beginner/03_keyword_search_by_hand/lesson.py
```

## Expected output

```
Query: 'What is firmware build 20240115 for?'
   8  home_network.md
   8  old_travel_router.md
   3  espresso_machine.md
   2  3d_printer.md
   1  houseplants.md
   0  bike_maintenance.md

Query: 'Why does it happen and what should I do about it?'
  13  bike_maintenance.md
  11  old_travel_router.md
   9  home_network.md
   8  houseplants.md
   7  3d_printer.md
   6  espresso_machine.md
```

Two flaws, one algorithm. On the firmware question, `home_network.md`
(the right document, contains `20240115`) and `old_travel_router.md`
(the wrong one, contains a different build number, `20210830`) tie at 8
apiece. Raw counting has no way to know that `20240115` is the one
distinguishing token, it counts "firmware" and "build," words both
documents share, exactly as heavily as the one word that actually
separates them. On the second question, built entirely out of common
words ("what," "do," "it," "about"), every document scores high and the
ranking is close to meaningless, whichever document happens to be
longest or use those common words most often wins, not whichever
document is actually relevant.

## Checkpoint

- **Sparse retrieval**: matching on exact tokens, no embedding model, no
  notion of "meaning."
- **Raw term frequency**: count query-token occurrences per document, sum
  them, rank by the total. Simple, and decisive on rare, distinctive
  tokens.
- **The flaw**: common words count exactly as much as rare ones, so a
  question full of ordinary language barely discriminates at all, and
  two documents that share common words but differ on the one rare,
  distinguishing token can tie outright. Fixed next lesson.

If anything here still feels unclear, ask before moving to Lesson 4.
