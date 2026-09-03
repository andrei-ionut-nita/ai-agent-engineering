# Lesson 21: Metadata Filtering by Modality

## Where we left off

Lesson 20 stored `modality` as chromadb metadata but never used it in a
query. `naive_rag` Lesson 22 narrowed a chromadb query with `where`
filters on `source`/`area`; this lesson applies the identical mechanism
to `modality`, letting a caller ask for text-only results, image-only
results, or both (the default), a scoping tool Lesson 13's Python-level
balancing didn't have: "only images, ever, for this query" rather than
"some of each, ranked separately."

## Why this is different from Lesson 13's k-balancing

Lesson 13 guarantees representation from *both* modalities in one
result set. This lesson does the opposite kind of thing: excluding a
modality entirely, useful when a caller already knows the answer must
be visual (a UI button labeled "search diagrams only", say) rather than
letting the ranking decide. Both tools solve different problems;
neither replaces the other.

## The code, piece by piece

```python
def query_collection(
    collection: chromadb.Collection,
    query_vector: list[float],
    n_results: int,
    modality: str | None = None,
) -> dict:
    where = {"modality": modality} if modality else None
    return collection.query(query_embeddings=[query_vector], n_results=n_results, where=where)
```

`naive_rag` Lesson 22's exact pattern: build a `where` clause only when
a filter is actually requested (`None` means "no filter, search
everything"), pass it straight to `.query()`. `modality` being one of
exactly two string values (`"text"`, `"image"`) makes this filter
trivial to reason about, unlike a filter over a large, open-ended set of
`source` values.

## Running it

```bash
uv run python lessons/multimodal_rag/03_advanced/21_metadata_filtering_by_modality/lesson.py
```

## Expected output

```
Query: "What does the setup look like?"

Unfiltered top match: home-observatory.md (modality=text)
Filtered to modality='image': observatory-finder-scope.png (modality=image)
```

## Checkpoint

- `where={"modality": "image"}` scopes a chromadb query to one
  modality, the same filtering mechanism `naive_rag` Lesson 22 used for
  `source`/`area`, applied to this course's one new metadata dimension.
- This is a different tool from Lesson 13's balancing: excluding a
  modality entirely versus guaranteeing a mix from both.

If anything here still feels unclear, ask before moving to Lesson 22.
