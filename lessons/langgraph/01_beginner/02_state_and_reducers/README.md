# Lesson 2: State merges by default, but some fields need to accumulate

## Where we left off

Lesson 1's state had one field, and one node that overwrote it. Real
graphs almost always have more than one field, and more than one node
touching state over the course of a run. This lesson adds a second
field and asks: when two different nodes both write to state, what
actually happens to the data?

## Partial updates get merged, not replaced

Here's the rule, stated precisely, because it matters for everything
that follows: when a node returns `{"some_field": value}`, LangGraph
does not throw away the rest of the state and replace it with just that
dictionary. It merges the returned dictionary into the existing state,
key by key. If a node doesn't mention a field in what it returns, that
field is left exactly as it was.

By default, when a field IS mentioned, the new value simply replaces
the old one, last write wins. That's fine for most fields (like Lesson
1's `text`, only one node ever touched it). But some fields are meant to
grow over the course of a run instead of being replaced, a log of steps
taken, a running list of messages, and so on. For those, plain
last-write-wins is wrong, you'd lose everything written before.

## Introducing reducers

```python
class GraphState(TypedDict):
    text: str
    history: Annotated[list[str], operator.add]
```

`history` is still just a list under the hood, but it's wrapped in
`Annotated[list[str], operator.add]`. `Annotated` lets you attach extra
metadata to a type hint without changing the type itself, here the
"extra metadata" is `operator.add`, a function LangGraph calls a
**reducer**.

Whenever a node returns a value for `history`, LangGraph doesn't just
overwrite the old list with the new one. It calls the reducer:
`operator.add(old_history, new_history)`. For lists, `operator.add` is
just `+`, list concatenation, so the new items get appended to the old
ones instead of replacing them. `text`, with no `Annotated` wrapper, has
no reducer, it keeps the default last-write-wins behavior from Lesson 1.

## The code, piece by piece

```python
def clean(state: GraphState) -> dict:
    return {"text": state["text"].strip(), "history": ["cleaned"]}


def shout(state: GraphState) -> dict:
    return {"text": state["text"].upper(), "history": ["shouted"]}
```

Two nodes, each doing one small transformation to `text` (overwritten
each time, exactly like Lesson 1) and each appending one word to
`history` (accumulated, because of the reducer). Notice each node only
returns `["cleaned"]` or `["shouted"]`, a single-item list, not the
whole growing history, the reducer is what's responsible for growing it.

```python
builder.add_edge(START, "clean")
builder.add_edge("clean", "shout")
builder.add_edge("shout", END)
```

Two nodes chained one after another (Lesson 3 goes further with this
idea). By the time this reaches `END`, `text` reflects only the last
node that touched it (`shout`'s uppercase version), while `history` has
accumulated an entry from both nodes.

## Running it

```bash
uv run python lessons/langgraph/01_beginner/02_state_and_reducers/lesson.py
```

Watch the printed `history` list, it will contain `["cleaned",
"shouted"]`, even though each node individually only ever returned a
single-item list.

## Checkpoint

- **merge, not replace**: a node's returned dict is merged into state
  field by field, fields the node didn't mention are left untouched.
- **last-write-wins**: the default behavior for a plain field, a new
  value fully replaces the old one.
- **reducer**: a function (`operator.add` here) that decides how a new
  value combines with the old one, instead of just replacing it.
- **`Annotated[type, reducer]`**: how you attach a reducer to a state
  field's type hint.

If anything here still feels unclear, ask before moving to Lesson 3.
