# Lesson 19: Checkpoint — Reporting Chain Finder

## What this is

A small script combining this tier's two traversal-shaping tools,
`edge_types` and `filter`, into one reporting-structure report for a
person: their full management chain up to the top, and which of their
direct/indirect reports are senior enough (3+ years) to matter for a
succession conversation.

## What it does

`management_chain(conn, person_id)` walks `reports_to` outward
(subordinate to manager to manager's manager) with `graph.traverse()`,
unfiltered, since you want the whole chain regardless of seniority.
`senior_reports(conn, person_id, min_years)` walks the same edge type
*inward* (manager to reports), this time with a `graph.gte()` filter on
`seniority_years`. `main()` runs both for Dan and prints a small report.

## Where each piece came from

- Schema setup (companies with subsidiaries, people with a reporting
  chain, projects), table/edge/filter-column registration,
  `graph.build()` — Lesson 10's `setup_and_build()`, reused as-is.
- `management_chain()` — `graph.traverse()` with `edge_types :=
  ARRAY['reports_to']`, `direction := 'out'`, from Lesson 10.
- `senior_reports()` — the same call shape, `direction := 'in'`, plus
  `filter := graph.gte('seniority_years', min_years)` from Lesson 11.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/02_intermediate/19_intermediate_checkpoint_project/lesson.py
```

## Expected output

```
Management chain for Dan (up to the top):
  depth=1  Bob (p2)
  depth=2  Alice (p1)

Dan's reports with 3+ years of seniority:
  (none, Dan doesn't manage anyone senior enough)

Management chain for Alice (up to the top):
  (none, they're already at the top)

Alice's reports with 3+ years of seniority:
  depth=1  Bob (p2), 6 years
```

## Try this yourself

- Give Dan a direct report in `setup_and_build()` (add a person with
  `manager_id := 'p4'`) and confirm they show up in
  `senior_reports(conn, 'p4', 3)` if their seniority qualifies.
- Lower `min_years` to `1` for Alice's report and confirm Dan (2 years,
  her indirect report) now appears too.
- Try `management_chain` on Eve (`p5`), who has no manager set, and
  confirm it returns an empty list rather than erroring.

If anything here still feels unclear, ask before moving to Lesson 20.
