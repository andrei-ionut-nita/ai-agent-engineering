# Lesson 18: Intermediate Checkpoint - Persisted, Filterable Hybrid Assistant

## What this is

No new concepts in this lesson. This is a checkpoint: everything from
Lessons 10 through 17 combined into one small, real assistant. If you
can read `lesson.py` and understand why every piece is there, you've
mastered the Intermediate tier.

## What it does

The same hybrid retrieval from Lesson 9's Beginner checkpoint, now with
three upgrades: the index is persisted to disk (Lesson 13) instead of
rebuilt every run, retrieval can be scoped to a category before fusing
(Lesson 12), and every answer cites its source, same as `naive_rag`'s
own notes-search assistant, just with a hybrid retriever underneath.

## Where each piece came from

```python
def load_or_build_store(notes_dir, store_path) -> dict:
    if store_path.exists():
        return json.loads(store_path.read_text())
    store = build_store(notes_dir)
    store_path.write_text(json.dumps(store))
    return store
```
Lesson 13, unchanged: load from disk if a saved index exists, build and
save it if not. Every question this script answers reuses the same
loaded index, no repeated embedding calls.

```python
def hybrid_retrieve(query, store, k=2, category=None):
    candidate_indices = [i for i, name in enumerate(store["names"]) if category is None or CATEGORY.get(name) == category]
    ...
```
Lesson 12's filter, applied before either retriever scores anything,
folded into the same function that does dense ranking, sparse ranking,
and RRF fusion, Lessons 2-8's full pipeline in one call.

```python
def ask(query, store, k=2, category=None) -> str:
    top_names = hybrid_retrieve(query, store, k, category)
    return generate(query, top_names, store)
```
The whole pipeline as one function call, same shape as Lesson 9's
`ask()`, now taking an optional category.

## Running it

```bash
uv run python lessons/hybrid_rag/02_intermediate/18_intermediate_checkpoint_project/lesson.py
```

Run it twice. The first run has no `store.json` yet and embeds every
document; the second loads the cached index instead, same behavior
Lesson 13 demonstrated on its own.

You should see three answers: a bare-ID question, a category-scoped
question that correctly distinguishes between this course's two router
notes when asked to compare them, and a paraphrased question, all cited.

## Try this yourself

Without looking anything up:

- Delete `store.json` and rerun. Does the first run's timing noticeably
  differ from the cached second run, the way Lesson 13 predicted?
- Ask `ask("20240115", store, category="kitchen")`, an ID whose real
  answer lives outside the category you scoped to. What does it return,
  and does that match what Lesson 12's filtering logic should do?
- Reuse Lesson 16's exact question (`"What change finally made things
  work reliably again?"`) through `ask()`. Does the generated answer
  correctly say it doesn't know, or does it guess? Compare that against
  what Lesson 16 already showed about where the retrieved chunk ranked.

If you can make these changes confidently, you're ready for the Advanced
tier, starting at Lesson 19.
