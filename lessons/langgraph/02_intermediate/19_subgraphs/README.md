# Lesson 19: subgraphs, a whole graph used as a single node

## The idea

Every graph in this course so far has been one flat collection of nodes.
As graphs grow, that stops scaling, a "summarize this document" pipeline
might itself deserve to be several nodes, but a bigger graph using it
shouldn't have to know or care about that internal structure. A
**subgraph** solves this: build a small graph, compile it, then hand the
compiled result straight to `add_node` on a bigger graph, as if it were
an ordinary function.

This is the same idea as agent-as-tool from the langchain course's
Lesson 31, wrapping a whole capability behind one clean interface, just
one level lower: here it's a whole *graph* behind one node, not a whole
*agent* behind one tool.

## Building the subgraph, nothing special about it

```python
summarize_builder = StateGraph(SummarizeState)
summarize_builder.add_node("summarize_node", summarize_node)
summarize_builder.add_node("count_words_node", count_words_node)
summarize_builder.add_edge(START, "summarize_node")
summarize_builder.add_edge("summarize_node", "count_words_node")
summarize_builder.add_edge("count_words_node", END)

summarize_subgraph = summarize_builder.compile()
```

Nothing here differs from any other graph you've built since Lesson 1.
It has its own state schema, its own nodes, its own edges, and it
compiles into a normal, independently runnable graph. You could call
`summarize_subgraph.invoke(...)` on its own right now and it would work.

## Plugging it into a bigger graph

```python
article_builder.add_node("summarize", summarize_subgraph)
```

This is the only new move: `add_node` normally takes a function, here it
takes a *compiled graph* instead. From `article_builder`'s perspective,
`"summarize"` is just another node, wire edges into and out of it
exactly like any other (`article_builder.add_edge(START, "summarize")`).

## Why this works without any translation code

```python
class SummarizeState(TypedDict):
    text: str
    summary: str
    word_count: int

class ArticleState(TypedDict):
    text: str
    summary: str
    word_count: int
    title: str
```

`SummarizeState`'s fields are a subset of `ArticleState`'s fields, same
names, same types. Because of that overlap, LangGraph can pass the
parent's state straight into the subgraph, and merge the subgraph's
output straight back into the parent's state, no adapter function
required. If the schemas didn't share field names, you'd wrap the
subgraph in a small function node that translates between the two
shapes on the way in and out, still simple, just an extra explicit step.
This lesson picked the shared-schema approach on purpose, for the
simplest version of the idea.

## Running it

```bash
uv run python lessons/langgraph/02_intermediate/19_subgraphs/lesson.py
```

`app.invoke(...)` here looks identical to invoking any flat graph in
this course, nothing about calling it reveals that `"summarize"` is
secretly two model calls wrapped inside its own compiled graph.

## Checkpoint

- **subgraph**: a compiled `StateGraph`, passed directly to a parent
  graph's `add_node` in place of a plain function.
- **shared-schema subgraphs**: when the subgraph's state fields are a
  subset of the parent's, state flows in and out automatically, no
  translation needed.
- **from the parent's view, it's just a node**: `.invoke()` on the
  parent graph behaves identically whether a node is a single function
  or an entire subgraph.
- **when schemas don't match**: wrap the subgraph in a small function
  node that translates state shapes on the way in and out.

If anything here still feels unclear, ask before moving to Lesson 20,
where a single node both updates state and decides where to go next.
