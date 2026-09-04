# Lesson 22: A route() and Strategy-Registry Pattern

## Where we left off

Lesson 21 proved all five real courses wire in the same way. This lesson
turns that into a clean, reusable shape: a `Strategy` registry (name to
ready state and real `ask()`), a plain dict routing table mapping a
label to a strategy name, and one small `route()` function, instead of
an `if label == "simple_factual": ... elif label == "multi_hop": ...`
chain that grows one branch every time a route is added.

## The code, piece by piece

```python
@dataclass
class Strategy:
    name: str
    state: object
    ask: Callable[[str, object, int], str]
```

Everything `route()` and `answer()` need to dispatch to a strategy by
name: the strategy's own already-built `State` (from Lesson 21's
`ingest()` calls, run once) and its real `ask()` function, bundled
together.

```python
ROUTES: dict[str, str] = {
    "simple_factual": "naive",
    "multi_hop": "graph",
    "ambiguous": "corrective",
}


def route(label: str) -> str:
    return ROUTES.get(label, "naive")
```

A plain dict, not a chain of conditionals. Adding a fourth or fifth
route (Lesson 25's capstone routes to all five strategies) means adding
one line to `ROUTES`, not a new `elif` branch and a new place for a bug
to hide.

```python
def answer(query: str, registry: dict[str, Strategy], k: int = 2) -> tuple[str, str]:
    label = classify(query)
    strategy_name = route(label)
    strategy = registry[strategy_name]
    return strategy_name, strategy.ask(query, strategy.state, k)
```

Classify, route, dispatch: three small, separately-testable steps
instead of one long function, each one doing exactly what its name says
and nothing else.

## Running it

```bash
uv run python lessons/adaptive_rag/03_advanced/22_a_route_and_strategy_registry_pattern/lesson.py
```

## Expected output

```
Building the strategy registry (naive, corrective, graph)...

Q: What oven setting does the pizza dough recipe use?
   routed to: naive
   A: <a grounded answer citing pizza-dough.md>

Q: What two hobbies happen in the same room as the weather station?
   routed to: graph
   A: <graph_rag's real traversal answer>

Q: How does wind speed affect things around the house?
   routed to: corrective
   A: <corrective_rag's real graded answer>
```

The classifier's exact label can vary run to run (it's a real model call,
not a lookup table), so a specific question routing to a different
strategy than shown above isn't a bug, it's the same honest classifier
variability Lesson 16 covers in more depth.

## Checkpoint

- A registry (`dict[str, Strategy]`) plus a routing table (`dict[str,
  str]`) replaces a growing conditional chain, and scales to five routes
  exactly as cleanly as it scales to three.
- `Strategy` bundles a name, a ready state, and a real `ask()` together,
  so `answer()` never needs to know which course a strategy came from,
  only that it satisfies the shared protocol.
- This is the shape Lesson 23's service wraps directly: `build_registry()`
  becomes startup work, `answer()` becomes the request handler.

If anything here still feels unclear, ask before moving to Lesson 23.
