# Lesson 8: Keeping stored embeddings in sync with source data

## Where we left off

Every prior lesson only inserted. Real data changes: a note gets
edited, a document gets removed. This lesson closes the loop, `UPDATE`
and `DELETE` on a table with a `vector` column work exactly like they
do on any other table, with one easy-to-miss trap.

## The trap: editing the text without re-embedding

```sql
UPDATE notes SET content = %s WHERE id = %s
```

This updates the text, but the `embedding` column still holds the
*old* text's vector. Nothing about SQL enforces that a `vector` column
stays consistent with some other column's meaning, that's on the
application to maintain. Search would now return this row for queries
matching its *old* content, silently wrong, no error anywhere.

## The fix: always re-embed on update

```python
new_content = "Recipe notes: the dough now uses whole wheat flour."
new_vector = Vector(embeddings_model.embed_query(new_content))

conn.execute(
    "UPDATE notes SET content = %s, embedding = %s WHERE id = %s",
    (new_content, new_vector, note_id),
)
```

Whenever the source text changes, the embedding call has to run again,
in the same update. There's no shortcut, the vector *is* a function of
the text, and Postgres has no way to know the embedding model exists.

## Deleting

```sql
DELETE FROM notes WHERE id = %s
```

Nothing pgvector-specific here at all, `DELETE` removes the row,
vector column included, exactly like any other row.

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/01_beginner/08_updating_and_deleting_vectors/lesson.py
```

## Checkpoint

- `UPDATE` and `DELETE` on a `vector` column work exactly like on any
  other column, no special syntax.
- Editing content without re-embedding leaves a stale vector that
  search will still match against, silently.
- The fix is always the same: re-run the embedding call as part of the
  same update whenever the underlying text changes.

If anything here still feels unclear, ask before moving to Lesson 9.
