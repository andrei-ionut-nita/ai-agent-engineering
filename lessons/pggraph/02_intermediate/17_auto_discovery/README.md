# Lesson 17: Auto-discovery, and why this course doesn't use it

## Where we left off

Every table and edge in this course so far was registered by hand,
`graph.add_table()`, `graph.add_edge()`, with labels and columns you
chose deliberately. pggraph also offers `graph.auto_discover()`, which
scans a schema and registers everything it can infer from foreign keys
automatically. This lesson shows the safe, read-only preview of what it
would do, and explains why the course keeps registering by hand anyway.

## `graph.preview_discover()`: a dry run

```sql
SELECT * FROM graph.preview_discover('public');
```

This scans the `public` schema and reports what it *would* register,
without registering anything. Run it against this course's schema and
it finds the same tables and foreign keys Lesson 10 registered by
hand, but with different edge labels: `company` instead of `works_at`,
`manager` instead of `reports_to`, `parent_company` instead of
`subsidiary_of`, derived mechanically from column names rather than
chosen for readability.

## Why this matters: `graph.auto_discover()` doesn't merge with your labels

The full (non-preview) `graph.auto_discover('public')` registers
tables and edges for real, and runs a build in the same call. If you'd
already registered `works_at` by hand, as this course has since Lesson
4, auto-discovery doesn't know that `people.company_id -> companies.id`
under the label `company` is "the same relationship" as your hand-named
`works_at`, it registers both, and your graph ends up with duplicate
edge types describing the same connection under two names. There's no
built-in way to remove a stale registration afterward either. Because
of that, this course's lesson scripts stick to explicit
`add_table`/`add_edge` calls throughout, and this lesson only ever runs
the non-mutating preview.

## When auto-discovery is the right call

On a schema pggraph has never touched, with foreign keys that already
say what you mean (`company_id`, not some abbreviation), auto-discovery
can save real setup time, that's what it's for. Preview it first with
`graph.preview_discover()` regardless, so you know what labels you're
about to get before anything is registered.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/02_intermediate/17_auto_discovery/lesson.py
```

## Expected output

```
preview_discover('public') would register:
  table  companies                                    pk=id, columns=[name, parent_company_id]
  table  people                                       pk=id, columns=[name, company_id, manager_id]
  table  projects                                     pk=id, columns=[name, lead_person_id]
  edge   companies.parent_company_id → companies.id   label=parent_company, bidirectional=true
  edge   people.company_id → companies.id             label=company, bidirectional=true
  edge   people.manager_id → people.id                label=manager, bidirectional=true
  edge   projects.lead_person_id → people.id          label=lead_person, bidirectional=true
```

## Checkpoint

- **`graph.preview_discover(schema_name)`**: read-only, shows what
  auto-discovery would register, changes nothing.
- **`graph.auto_discover(schema_name)`**: registers and builds for real;
  doesn't merge with or replace prior hand-made registrations under
  different labels, it adds alongside them.
- **this course's choice**: hand-picked labels via `add_table`/`add_edge`
  throughout, specifically to keep edge names readable and avoid this.

If anything here still feels unclear, ask before moving to Lesson 18.
