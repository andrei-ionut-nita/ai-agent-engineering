# Lesson 18: Querying runs with filters, and building a small dashboard

## What we're building

Two `client.list_runs(...)` queries: all `"chain"`-type runs in the
project, and just the ones tagged `"langsmith-course"`, then a handful
of aggregates (counts by function name, average latency, error count)
computed locally from what comes back.

## What this reveals

Every earlier lesson either traced something or evaluated something, but
none of them asked "show me everything that happened, filtered down to
what I actually care about." `list_runs` is that query: given a project
and an optional `filter` string, it returns every matching run as a
plain Python object, with `.name`, `.run_type`, `.start_time`,
`.end_time`, `.error`, `.tags`, and more, ready for whatever you want to
do with it.

The `filter` argument uses a small query language: `eq(field, value)`,
`gt`/`lt` for comparisons, `has(tags, "value")` for tag membership, and
`and()`/`or()` to combine conditions. This is the same filtering the
LangSmith UI's search bar uses, just callable from code.

Once you have a list of runs back, a "dashboard" is just aggregation:
counting, averaging, grouping, ordinary Python (or pandas, as in Lesson
15) over the returned objects. The UI's dashboards do exactly this,
this lesson does it by hand to show there's no magic underneath.

## The code, piece by piece

```python
chain_runs = list(client.list_runs(project_name=PROJECT_NAME, run_type="chain", limit=50))
```

`run_type="chain"` narrows to one kind of run (Lesson 3). `limit=50`
caps how many are fetched, `list_runs` returns a generator, wrapping it
in `list(...)` pulls everything into memory at once.

```python
by_name = Counter(run.name for run in chain_runs)
latencies = [(run.end_time - run.start_time).total_seconds() for run in chain_runs if run.end_time is not None]
error_count = sum(1 for run in chain_runs if run.error is not None)
```

Three independent aggregates over the same list: which functions ran
most often, how long runs took on average, how many failed. Each of
these is a real question you'd ask about a production system, answered
here from data that was already being recorded anyway.

```python
course_runs = list(client.list_runs(project_name=PROJECT_NAME, filter='has(tags, "langsmith-course")', limit=50))
```

The filter query language in action: `has(tags, "langsmith-course")`
matches any run whose tags include that value, narrowing from "every
chain run" to specifically the ones this course's own lessons produced.

## Running it

```bash
uv run python lessons/langsmith/03_advanced/18_filtering_and_dashboards/lesson.py
```

Run a few earlier lessons first if you haven't already, so there's
something to query. You should see counts per function name, an average
latency, an error count, and a separate count of runs tagged
`"langsmith-course"`.

## Checkpoint

- **`client.list_runs(project_name, run_type=, filter=, limit=)`**:
  queries runs directly, the programmatic equivalent of the UI's search.
- **Filter query language**: `eq`/`gt`/`lt`/`has`, combined with
  `and()`/`or()`, for narrowing which runs come back.
- **Dashboards are aggregation**: once you have runs back as objects,
  building a dashboard is ordinary counting/averaging/grouping over
  their fields.

If anything here still feels unclear, ask before moving to Lesson 19.
