# Lesson 13: Persisting Routing Decisions

## Where we left off

Every lesson so far printed its routing decision and then threw it
away, the next run starts from nothing, and there's no way to ask "how
often does this classifier reach for the corrective route?" without
re-running everything and reading the terminal by hand. This lesson
logs each decision, question, label, confidence, strategy, and what got
retrieved, to a local file that survives between runs.

## Why JSON Lines, not one big JSON array

A single JSON array (`[{...}, {...}, {...}]`) needs the whole file
rewritten every time a new entry is added, and a crash mid-write can
corrupt the entire log, not just the newest entry. **JSON Lines**
(`.jsonl`, one complete JSON object per line) sidesteps both problems:
a new entry is one `open(..., "a")` append and one line written, every
earlier line is untouched, and the worst a mid-write crash can do is
leave one unfinished trailing line, everything before it stays valid.

## The code, piece by piece

```python
def log_decision(entry: dict) -> None:
    with LOG_PATH.open("a") as f:
        f.write(json.dumps(entry) + "\n")
```

`"a"` (append mode) is the whole trick: every call opens the file, adds
one line at the end, and closes it, no read-modify-write of the rest of
the file required.

```python
entry = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "question": question,
    "label": label,
    "confidence": confidence,
    "strategy": strategy,
    "sources_retrieved": [r["source"] for r in retrieved],
}
```

Every field needed to reconstruct "what happened and why" for this one
decision, without re-running anything: what was asked, what label and
confidence the classifier gave it, which strategy actually ran, and
what came back.

## Running it

```bash
uv run python lessons/adaptive_rag/02_intermediate/13_persisting_routing_decisions/lesson.py
```

## Expected output

```
Q: What oven setting does the pizza dough recipe use?
  label: simple_factual (confidence=1.00)
  strategy: naive
  sources: ['pizza-dough.md']

Q: What two hobbies happen in the same room as the weather station?
  label: multi_hop (confidence=0.95)
  strategy: multi_hop
  sources: ['bookshelf.md', 'weather-station.md']

Q: How does wind speed affect things around the house?
  label: ambiguous (confidence=0.85)
  strategy: corrective
  sources: ['garden.md', 'weather-station.md']

--- routing_log.jsonl, 3 lines ---
{"timestamp": "...", "question": "...", "label": "simple_factual", ...}
{"timestamp": "...", "question": "...", "label": "multi_hop", ...}
{"timestamp": "...", "question": "...", "label": "ambiguous", ...}
```

Each printed decision has a matching line in `routing_log.jsonl`, and
that file keeps growing across separate runs of the script (this
lesson's `main()` clears it first only so the demo output stays
readable; a real deployment would just keep appending).

## Checkpoint

- **JSON Lines (`.jsonl`)**: one JSON object per line, appended, not
  rewritten, the simplest durable format for a log that only ever
  grows.
- Logging a routing decision at the moment it happens means later
  analysis (which strategy runs most often, what confidence looks like
  per label) needs no re-running, just reading the file back.
- This log is intentionally simple, a list of flat dicts, no schema
  migrations, no database, matching this course's own "hand-rolled,
  nothing hidden" approach the same way `naive_rag`'s intermediate tier
  persists its own vector store as plain JSON.

If anything here still feels unclear, ask before moving to Lesson 14.
