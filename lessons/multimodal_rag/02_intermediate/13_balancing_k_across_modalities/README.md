# Lesson 13: Balancing k Across Modalities

## Where we left off

Every retrieval so far ranked the whole mixed store by similarity and
took the top `k`, with no regard for modality. That's usually fine, but
it has a real failure mode: if a corpus has far more text chunks than
image captions (very common; one document might have five paragraphs
and one figure), a plain top-`k` search can let text chunks crowd out a
genuinely relevant image simply because there are more text records in
the pool competing for the same `k` slots, not because the image scored
lower on merit for any single comparison. This lesson demonstrates that
crowding-out directly, then fixes it with **per-modality k**.

## The code, piece by piece

```python
def retrieve_balanced(query: str, store: list[dict], k_text: int, k_image: int) -> list[dict]:
    query_vector = embed_texts([query])[0]
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    text_hits = sorted(
        (r for r in scored if r["modality"] == "text"), key=lambda r: r["score"], reverse=True
    )[:k_text]
    image_hits = sorted(
        (r for r in scored if r["modality"] == "image"), key=lambda r: r["score"], reverse=True
    )[:k_image]
    return text_hits + image_hits
```

Instead of one ranked list and one `k`, split scored records by
`modality` (Lesson 11) first, rank each group separately, and take a
fixed number from *each*. `k_text=2, k_image=1` guarantees at least one
image gets through regardless of how many text chunks scored slightly
higher overall, exactly the guarantee plain top-`k` doesn't make.

```python
plain = retrieve(query, store, k=3)
balanced = retrieve_balanced(query, store, k_text=2, k_image=1)
```

Run both against the same query and compare which modalities show up
in each. On a query where the right image scores just below several
text chunks, plain top-`k` drops it entirely; balanced retrieval keeps
it, by construction, not by luck.

## Running it

```bash
uv run python lessons/multimodal_rag/02_intermediate/13_balancing_k_across_modalities/lesson.py
```

## Expected output

```
Query: "What does the closed terrarium look like when it's working correctly?"

Plain top-3 (unbalanced): ['terrarium.md', 'circuit-board.md', 'sourdough-starter.md'] (0 images)
Balanced (k_text=2, k_image=1): ['terrarium.md', 'circuit-board.md', '<some image>.png'] (1 image, guaranteed)
```

## Checkpoint

- Plain top-`k` over a mixed store can let one modality crowd out the
  other, not because of a bad ranking, just because one modality has
  more competing records in the pool.
- Balancing k means ranking each modality's candidates separately and
  taking a fixed slice from each, guaranteeing representation instead
  of hoping for it.
- This trades away "always the single highest-scoring k records
  overall" for "a guaranteed mix", worth it whenever a real answer is
  likely to need both a text fact and an image fact together (Lesson
  14's citation style depends on this).

## Try this yourself

Without looking anything up:

- Set `k_image=0` on a question that genuinely needs an image. Confirm
  the answer degrades exactly the way Lesson 2's text-only pipeline
  did, on purpose, then set it back.
- Try `k_text=1, k_image=1` on the sourdough starter question from
  Lesson 9, does the combined text+image context still answer the full
  question, or does dropping to one text chunk lose something?

If anything here still feels unclear, ask before moving to Lesson 14.
