# Lesson 5: edges decide the order, not the layout

## Where we left off

Lesson 4's flow ran Chat Input, then Prompt, then Gemini, then Chat
Output, in that order, left to right on the canvas. It's tempting to
assume that's *because* they're arranged left to right. This lesson
shows that's a coincidence: what actually decides run order is the
edges, full stop.

## Do this yourself

Reopen Lesson 4's flow (still in your browser).

1. Drag the **Chat Output** node so it sits on the far left, and drag
   **Chat Input** to the far right, physically reversing their layout.
2. Open the **Playground** and run it again. Confirm it behaves exactly
   the same, Chat Input still runs first, Chat Output still runs last,
   despite Chat Output now sitting to the *left* of Chat Input on
   screen.
3. Drag the nodes back into a sensible layout (or don't, it doesn't
   affect behavior at all).

## Why this is true

A flow's real shape lives in its edges: "Prompt's `user_input` reads
from Chat Input's output" is a fact about a connection, not about pixel
coordinates. Langflow (and, underneath, `lfx`) computes run order with
a **topological sort**: it looks at every edge, and produces an order
where each component runs only after everything it depends on has
already run. Position on the canvas is purely for you, the human
reading the flow, to make its shape easier to see.

## The code, piece by piece

```python
chat_output = ChatOutput()
chat_input = ChatInput()
prompt = PromptComponent()
prompt.set(template="{user_input}", user_input=chat_input.message_response)
chat_output.set(input_value=prompt.build_prompt)
```

These four lines instantiate `ChatOutput` *before* `ChatInput`, on
purpose, the reverse of every earlier lesson. The `.set()` calls still
correctly say "Prompt reads from Chat Input" and "Chat Output reads
from Prompt", those connections are what matters, not which line came
first in the file.

```python
graph = Graph(start=chat_input, end=chat_output)
graph.prepare()
order = [vertex.display_name for vertex in graph.topological_sort()]
```

`topological_sort()` is the same computation the canvas uses to decide
run order, walking the edges to find a valid sequence. It doesn't know
or care that `ChatOutput()` was instantiated first in this file, it
only reads the connections.

## Running it

```bash
uv run python lessons/langflow/01_beginner/05_connecting_and_reordering/lesson.py
```

## Expected output

Exact, this is graph structure, not a model call:

```
Execution order (by edges, not by definition order):
  1. Chat Input
  2. Prompt Template
  3. Chat Output
```

## Checkpoint

- **edges are the real shape of a flow**, canvas position and Python
  definition order are both just presentation, neither affects
  behavior.
- **topological sort**: the algorithm that turns "who depends on whom"
  (the edges) into a valid run order, used by both the canvas and
  `Graph.topological_sort()`.

If anything here still feels unclear, ask before moving to Lesson 6.
