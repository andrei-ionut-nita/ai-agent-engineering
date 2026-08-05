# Lesson 11: Seeing the shape of the graph you built

## Where we left off

Ten lessons in, you've been building graph shapes by reading a series
of `add_node`/`add_edge`/`add_conditional_edges` calls and mentally
picturing the resulting shape. That gets harder fast once a graph has a
dozen nodes and several branches. LangGraph can print the shape it
actually compiled, so you can check it matches what you meant to build,
this becomes genuinely useful debugging once graphs get bigger, later
in this course.

## The code, piece by piece

```python
print(app.get_graph().draw_mermaid())
```

`app.get_graph()` returns a representation of the compiled graph's
structure, every node and every edge, including the conditional ones.
`.draw_mermaid()` renders that structure as Mermaid diagram source, a
small text-based diagram language, as plain text. It needs no extra
dependencies and always works, so it's the method this lesson leans on.
You can paste the printed output into any Mermaid renderer (many
Markdown viewers, including GitHub, render `mermaid` code fences
automatically) to see the actual picture.

```python
app.get_graph().draw_mermaid_png()
```

If you want an actual image file instead of text you paste elsewhere,
`.draw_mermaid_png()` returns PNG bytes directly, write them to a file
with `open("graph.png", "wb").write(png_bytes)`. This needs additional
dependencies to render remotely and isn't guaranteed to work in every
environment, so treat it as an optional aside, `.draw_mermaid()` is the
one to reach for by default.

## Reading the output against the code that produced it

We rebuild Lesson 7's think/act loop (`call_model` routing to either
`tools` or ending, `tools` routing back to `call_model`) specifically
because it has both a branch and a cycle, the two shapes hardest to
picture just from reading `add_edge` calls in order. Look at the printed
Mermaid source and confirm you can find: the `START` arrow into
`call_model`, the branch out of `call_model` (one path to `tools`, one
to `END`), and the edge from `tools` back to `call_model` that makes it
a loop. Being able to cross-reference a printed diagram against the code
that built it is the actual skill here, useful the moment a graph is
too big to hold entirely in your head.

## Running it

```bash
uv run python lessons/langgraph/01_beginner/11_visualizing_the_graph/lesson.py
```

## Checkpoint

- **`app.get_graph()`**: returns the compiled graph's structure, nodes
  and edges, including conditional ones.
- **`.draw_mermaid()`**: renders that structure as Mermaid diagram
  source text, no extra dependencies, paste it into a Mermaid renderer
  to see the picture.
- **`.draw_mermaid_png()`**: an optional alternative that returns actual
  PNG image bytes, needs more setup, not the default choice here.
- **cross-checking**: reading a printed diagram back against the
  `add_node`/`add_edge` calls that produced it is how you verify a
  graph's shape matches what you intended, especially once it's too big
  to picture from code alone.

If anything here still feels unclear, ask before moving to Lesson 12,
the beginner tier's checkpoint project.
