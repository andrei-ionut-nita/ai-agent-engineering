# Lesson 18: Keeping the graph current after row changes

## Where we left off

Every lesson so far called `graph.build()` once and queried a graph
that never changed underneath it. Real data changes: someone gets a
new manager, a company gets acquired. This lesson looks at what
actually happens to query results when the underlying tables change,
which turns out to be less dramatic than "you must rebuild."

## Recall: `sync_mode = 'trigger'`, from Lesson 5

`graph.build()` installs triggers on every registered table by default
(Lesson 5's warning about it). Those triggers queue up a record of
every insert/update/delete, visible in `graph.status()` as
`pending_sync_rows`.

## Writes are visible immediately, before you sync anything

This is the part worth being precise about, because it's easy to
assume otherwise: a change to a registered table shows up in traversal
results *before* you call anything sync-related.

```sql
-- Carol doesn't report to anyone yet
UPDATE people SET manager_id = 'p1' WHERE id = 'p3';

-- Immediately reflects Carol reporting to Alice, no sync call yet
SELECT node_id FROM graph.traverse(
  seed_table := 'public.people'::regclass, seed_id := 'p1',
  max_depth := 2, edge_types := ARRAY['reports_to'], direction := 'in'
);
```

The traversal engine checks a pending-change overlay on every query
(the README's own architecture notes call this "sync overlays"), on
top of the compiled CSR structure, so recent writes are already
included. `graph.status()`'s `pending_sync_rows` confirms there's
something queued (`1`, right after the update above).

## `graph.apply_sync()`: folding the overlay in, not making it visible

```sql
SELECT * FROM graph.apply_sync();
-- inserts_applied=0  updates_applied=0  deletes_applied=0
```

What this actually does is merge the pending-change overlay into the
base compiled structure and clear the queue,
`pending_sync_rows` goes back to `0`. It's a maintenance step for
keeping queries fast as the overlay grows, not a prerequisite for
correctness, the data was already correct before you called it. Left
unapplied indefinitely, every query pays the cost of checking a larger
and larger overlay; `graph.status()`'s `sync_lag` is what you'd watch
in production to know when it's worth running.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/02_intermediate/18_incremental_sync/lesson.py
```

## Expected output

```
Reports to Alice, before Carol's manager change: ['p1', 'p2', 'p4']
pending_sync_rows after the UPDATE (no sync yet): 1
Reports to Alice, immediately after the UPDATE: ['p1', 'p2', 'p3', 'p4']
apply_sync: inserts=0, updates=0, deletes=0
pending_sync_rows after apply_sync: 0
```

(Alice's own ID shows up in her own "who reports to me" list, that's
`graph.traverse()`'s `include_start` defaulting to `true`, not a bug,
this course's other traversal examples pass `include_start := false`
explicitly when they don't want that.)

## Checkpoint

- **writes are visible immediately**: pggraph checks a pending-change
  overlay on every query, on top of the compiled graph.
- **`graph.apply_sync()`**: merges that overlay into the base compiled
  structure and clears `pending_sync_rows`, a maintenance step, not a
  correctness requirement.
- **`sync_lag`**: what to watch in production to know when the overlay
  has grown large enough that applying sync is worth the cost.

If anything here still feels unclear, ask before moving to Lesson 19.
