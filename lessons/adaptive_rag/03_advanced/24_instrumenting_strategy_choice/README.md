# Lesson 24: Instrumenting Strategy Choice

## Where we left off

Lesson 23's service returns an answer and which strategy produced it,
but that information disappears the moment the response is sent, nothing
records it anywhere. This lesson adds a routing log: every request's
question, classified label, the classifier's stated reason, which
strategy handled it, and how long the whole thing took, recorded and
retrievable.

## The code, piece by piece

```python
@dataclass
class RoutingLogEntry:
    question: str
    label: str
    reason: str
    strategy: str
    latency_seconds: float


ROUTING_LOG: list[RoutingLogEntry] = []
```

Lesson 13's persisted-decision idea (question, decision, outcome, saved
for later analysis), moved from a script's local list into the service
every request now runs through. `reason` comes from extending the
classifier prompt to return a short justification alongside its label,
not a separate call.

```python
entry = RoutingLogEntry(
    question=query, label=label, reason=reason, strategy=strategy_name, latency_seconds=round(elapsed, 2)
)
ROUTING_LOG.append(entry)
print(f"[routing log] {json.dumps(asdict(entry))}")
```

Every call to `answer()` appends one entry and prints it, so the log is
visible in real time (useful for a real deployment's log aggregator)
and also queryable afterward.

```python
@app.get("/logs")
def logs_endpoint() -> list[dict]:
    return [asdict(entry) for entry in ROUTING_LOG]
```

A second endpoint exposing the whole log, so "why did this question get
routed the way it did" is answerable after the fact, not only by reading
console output at the moment it happened.

## Running it

```bash
uv run python lessons/adaptive_rag/03_advanced/24_instrumenting_strategy_choice/lesson.py
```

## Expected output

```
[routing log] {"question": "What oven setting does the pizza dough recipe use?", "label": "simple_factual", "reason": "...", "strategy": "naive", "latency_seconds": 1.2}
GET /ask?q='What oven setting does the pizza dough recipe use?'
  {'answer': '...', 'strategy': 'naive', 'reason': '...'}
...
GET /logs
  [{'question': '...', 'label': 'simple_factual', ...}, {'question': '...', 'label': 'ambiguous', ...}]
```

The classifier's exact label can vary run to run, so a specific
question's label or strategy may differ from a previous run, the same
honest variability Lesson 16 covers in more depth.

## Checkpoint

- A routing log turns "which strategy handled this, and why" from
  something only visible in a single response into something
  retrievable afterward, across every request the service has handled.
- Extending the classifier prompt to return a `reason` field alongside
  its `label` costs nothing extra (same call, one more JSON field), and
  is what makes Lesson 15's "disclose the strategy and why" idea work at
  the service layer instead of only inside a single script's output.
- `/logs` is this lesson's whole instrumentation surface: a second,
  read-only endpoint over the same in-memory list every request already
  appends to.

If anything here still feels unclear, ask before moving to Lesson 25.
