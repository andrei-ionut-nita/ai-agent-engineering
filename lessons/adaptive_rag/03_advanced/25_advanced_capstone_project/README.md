# Lesson 25: Advanced Capstone - A Complete Adaptive RAG Service

## What this is

No new concepts in this lesson. This is the course's capstone: a small,
real FastAPI service built entirely out of ideas from Lessons 1 through
24, combined into one thing, with the strategy registry finally widened
from Lessons 22-24's three strategies to all five this series built:
naive, hybrid, graph, corrective, and agentic. If you can read
`lesson.py` and understand why every piece is there, you've mastered
this course.

## What it does

Builds all five real strategies at startup (Lesson 21's finding: every
one of them wires in with the argument shape its own course's Lesson 23
already defined), then serves a `GET /ask` endpoint that classifies each
question into one of five labels, routes it to the strategy that
matches, and returns the answer alongside which strategy handled it and
why, the same disclosure Lesson 24's instrumentation already built.

## Where each piece came from

```python
ROUTES: dict[str, str] = {
    "simple_factual": "naive",
    "keyword_or_id_lookup": "hybrid",
    "multi_hop": "graph",
    "ambiguous": "corrective",
    "needs_computation_or_tool": "agentic",
}
```

Lesson 22's registry pattern, widened from three routes to five. Each
route matches the specific strength Lesson 2 recapped for that course:
naive for a clean single-fact lookup, hybrid for a keyword/term-anchored
query (hybrid_rag's own Lesson 6 case: retrieval that hinges on close-to-
literal matching, not just semantic similarity), graph for multi-hop,
corrective for an ambiguous question that benefits from a grade-and-retry
check, and agentic for anything needing a tool call (arithmetic, in this
capstone's demo) rather than retrieval alone.

```python
DEMO_QUESTIONS = [
    "What oven setting does the pizza dough recipe use?",
    "What is the windowpane test used for when mixing pizza dough?",
    "What two hobbies happen in the same room as the weather station?",
    "How does wind speed affect things around the house?",
    "The pizza dough's cold ferment takes 48 hours. How many hours is that doubled?",
]
```

Five questions, deliberately one per strategy, so a single run of this
capstone provably exercises all five real implementations, not just
whichever one the classifier happens to favor.

```python
print(f"All five strategies used: {strategies_used == set(ROUTES.values())}")
```

A direct check on that claim: this line prints `True` when the run's
five demo questions genuinely routed to five distinct strategies.

## Running it

```bash
uv run python lessons/adaptive_rag/03_advanced/25_advanced_capstone_project/lesson.py
```

To run it as a real, live server: `uvicorn lesson:app --reload` from
this folder, then `curl "http://127.0.0.1:8000/ask?q=..."`.

## Expected output

```
GET /ask?q='What oven setting does the pizza dough recipe use?'
  {'answer': '...', 'strategy': 'naive', 'reason': '...'}

GET /ask?q='What is the windowpane test used for when mixing pizza dough?'
  {'answer': '...', 'strategy': 'hybrid', 'reason': '...'}

GET /ask?q='What two hobbies happen in the same room as the weather station?'
  {'answer': '...', 'strategy': 'graph', 'reason': '...'}

GET /ask?q='How does wind speed affect things around the house?'
  {'answer': '...', 'strategy': 'corrective', 'reason': '...'}

GET /ask?q='The pizza dough's cold ferment takes 48 hours. How many hours is that doubled?'
  {'answer': '...96...', 'strategy': 'agentic', 'reason': '...'}

Strategies exercised this run: ['agentic', 'corrective', 'graph', 'hybrid', 'naive']
All five strategies used: True
```

The classifier's exact label choice can vary between runs (it's still a
model call, not a lookup table), so if a run's `strategies_used` set
comes back smaller than five, that's the classifier disagreeing with
this README's expectation for a given question, not a bug in the
routing mechanism itself, worth comparing against Lesson 16's failure
modes if it happens.

## Try this yourself

Without looking anything up:

- Add a sixth demo question of your own targeting a strategy you think
  it should hit, does the classifier agree with your intent?
- Run `uvicorn lesson:app --reload` from this folder and hit `GET
  /ask?q=...` and `GET /logs` from a browser or `curl`, confirm the
  service behaves identically to the `TestClient` calls in the script.
- Compare this capstone's five-way `ROUTES` against Lesson 22's
  three-way version, what's identical, and what had to change to add
  hybrid and agentic cleanly?

This is where Adaptive RAG, and this entire series, ends up: five
architectures built by hand across seven courses, composed behind one
small, real, self-disclosing service. Lesson 26 is a short, code-free
look back at how all seven courses connect.
