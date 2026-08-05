# Lesson 25: Putting sync on a schedule instead of calling it by hand

## Where we left off

Lesson 18 called `graph.apply_sync()` by hand, right after a write.
Lesson 24 chained sync and vacuum into `graph.maintenance()`, still a
manual call. This lesson makes that automatic: a durable policy, run by
a scheduled background job, no application code calling anything.

## `graph.add_sync_policy()`

```sql
SELECT policy_id, job_id, schedule_interval_secs, enabled
FROM graph.add_sync_policy('default', schedule_interval_secs := 60);
```

Registers a policy for the `'default'` graph: run sync every 60
seconds (or pass `max_sync_lag_rows` instead/as well, to trigger based
on how much is queued rather than a fixed interval). This returns both
a `policy_id` (the policy itself) and a `job_id`, pggraph uses the same
durable job-scheduling mechanism (backed by `pg_cron`, the extension
Lesson 1 noticed installed alongside `graph`) for sync policies as for
everything else in this lesson.

## `graph.run_due_jobs()`: what actually executes a policy

```sql
SELECT job_id, status, rows_applied FROM graph.run_due_jobs();
```

Policies don't run themselves, something has to call
`graph.run_due_jobs()` on a cadence, that's what `pg_cron` is for in
this image, it's already scheduled to call this periodically. Calling
it yourself (as this lesson's script does, with a 1-second policy
interval so it's immediately due) executes any policy whose
`next_run_at` has passed and reports what ran.

## `graph.sync_health()`: the field to actually watch

```sql
SELECT sync_mode, pending_sync_rows, apply_sync_recommended
FROM graph.sync_health();
```

A wide status view purpose-built for monitoring, `apply_sync_recommended`
and `maintenance_recommended` are pggraph's own opinion on whether
you're behind, based on `pending_sync_rows` and how large the mutable
overlay has grown. This is the function worth polling from outside the
database (a monitoring job, or an AI agent deciding whether its own
memory graph needs attention) rather than re-deriving that judgment
from raw counts yourself.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/03_advanced/25_sync_policies_and_scheduled_jobs/lesson.py
```

Note: `graph.add_sync_policy()` isn't cleared by `graph.reset()`, each
run of this script adds another policy, so `run_due_jobs()`'s job count
grows a little on every rerun. That's expected, not a bug, this is the
one lesson in the course where rerunning changes a printed count.

## Expected output

```
Sync policy created: schedule_interval_secs=1, enabled=True
Due jobs run: 1, all completed=True, total rows_applied=1
sync_health(): sync_mode=trigger, pending_sync_rows=0, apply_sync_recommended=False
```

## Checkpoint

- **`graph.add_sync_policy(graph_name, schedule_interval_secs, max_sync_lag_rows)`**:
  a durable, scheduled sync policy, not a one-off call.
- **`graph.run_due_jobs()`**: what actually executes due policies,
  already scheduled via `pg_cron` in this course's Docker image.
- **`graph.sync_health()`**: the monitoring-oriented view, with
  `apply_sync_recommended`/`maintenance_recommended` flags instead of
  raw counts you'd have to interpret yourself.

If anything here still feels unclear, ask before moving to Lesson 26.
