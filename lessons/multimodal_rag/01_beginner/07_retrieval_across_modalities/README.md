# Lesson 7: Retrieval Across Modalities

## Where we left off

Lesson 6 built one list holding both text chunks and image captions.
This lesson is the payoff: run the exact same `retrieve()` function
`naive_rag` has used since Lesson 6, unmodified, against that mixed
list, and watch it correctly retrieve an **image's caption**, not a
text chunk, for a question no text chunk can answer. This is the
lesson Lesson 2 set up: back then, text-only retrieval found the right
*document* but not the right *fact*. Here, retrieval finds the right
*record*, because the record it needs to find is no longer excluded
from the search.

## The code, piece by piece

```python
def retrieve(query: str, store: list[dict], k: int) -> list[dict]:
    query_vector = embed_texts([query])[0]
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    return scored[:k]
```

This function is copy-pasted from `naive_rag` Lesson 6, not rewritten,
not extended, not a single line different. That's not laziness, it's
the whole design claim of captioning-then-embed from Lesson 1: once
every record is `{text, embedding, ...}`, ranking by cosine similarity
genuinely does not care whether a record's `text` came from a Markdown
file or a caption. If this function needed to change to search across
modalities, captioning-then-embed would have failed at its one job.

```python
question = "What's the torque spec for the rear derailleur hanger bolt?"
retrieved = retrieve(question, store, k=1)
```

`bike-repair.md`'s own text never mentions a torque spec (Lesson 2
proved this the hard way). `derailleur-hanger-diagram.png`'s *caption*
does, because Lesson 4's captioning transcribed it. So the top-ranked
record here should be the image's caption record, identifiable by
`record["image_path"]` not being `None`, retrieval reaching a fact that
was, one lesson ago, provably unreachable.

## Running it

```bash
uv run python lessons/multimodal_rag/01_beginner/07_retrieval_across_modalities/lesson.py
```

## Expected output

```
Question: What's the torque spec for the rear derailleur hanger bolt?

Top match: derailleur-hanger-diagram.png (image, score=0.XX)
Caption: <caption text mentioning 8 Nm>

Compare: naive_rag-style text-only retrieval over fixtures/notes/ alone
would have surfaced bike-repair.md's text, which never states this fact.
```

If instead the top match is a text record, the fixture question or
caption likely needs adjusting, this is exactly the situation this
course's own verification pass (documented in
`docs/RAG-SERIES-PLAN/multimodal_rag/phase-a-authoring.md`) checks for.

## Checkpoint

- Retrieval across modalities needed **zero** new retrieval code, only
  a store whose records include image captions alongside text chunks.
- The record retrieved here would be structurally invisible to Lesson
  2's text-only store, it doesn't exist as a document, only as a
  caption of an image.
- `record["image_path"] is not None` is how later code (Lesson 8) tells
  "this came from an image" apart from "this came from a document",
  cheaply, without any change to how ranking works.

## Try this yourself

Without looking anything up:

- Ask "What color is the mount motor wiring for RA vs. DEC?" (answered
  only by `observatory-mount-wiring.png`). Does it retrieve correctly
  at `k=1`?
- Ask a question with an answer in both a note's text *and* an image's
  caption (for example, about the sourdough starter's feeding
  schedule, in `sourdough-starter.md`'s text, versus its jar markings,
  in the image). Which one ranks first, and does that match your
  intuition for which is more directly relevant?

If anything here still feels unclear, ask before moving to Lesson 8.
