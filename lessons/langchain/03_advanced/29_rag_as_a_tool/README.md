# Lesson 29: RAG as a tool, letting an agent search your documents

## Where we left off

Lesson 28 built a vector store and searched it manually, we wrote the
query ourselves and called `similarity_search` directly. This lesson
wraps that same search as a **tool**, the exact `@tool` pattern from
Lesson 13, so an agent can decide for itself, per question, whether it
even needs to search at all.

## The RAG tool

```python
@tool
def search_personal_notes(query: str) -> str:
    """Search the user's personal notes for information relevant to the
    query. Use this for questions about the user's projects, garden,
    recipes, hobbies, or anything that sounds like it might be
    documented in their personal notes rather than general knowledge."""
    results = vector_store.similarity_search(query, k=2)
    if not results:
        return "No relevant notes found."
    return "\n\n".join(result.page_content for result in results)
```

This should look familiar: it's the exact shape of every tool since
Lesson 13, a function, decorated with `@tool`, with a docstring
describing when to use it. The only thing new here is *what the tool
actually does internally*: instead of a calculator or a word counter,
this one runs Lesson 28's similarity search and hands back whatever
chunks it finds. From the agent's point of view, this is just another
tool, no different in kind from `calculator`.

## Notice the docstring is doing real work

```python
"""Search the user's personal notes for information relevant to the
query. Use this for questions about the user's projects, garden,
recipes, hobbies, or anything that sounds like it might be
documented in their personal notes rather than general knowledge."""
```

Recall from Lesson 13: **the AI never sees your implementation, only
the name, description, and arguments.** This docstring is doing the
actual work of telling the agent *when* this tool is relevant, personal,
specific, documented information, as opposed to general world knowledge
it already knows. A vague docstring here (like just `"""Search
notes."""`) would leave the agent guessing, and it might reach for this
tool unnecessarily, or fail to reach for it when it should.

## Two questions, two different outcomes

```python
ask("How often do I practice my cello, and for how long?")
ask("What is the capital of Japan?")
```

The first question can *only* be answered by actually searching
`notes.txt`, there's no other way the agent could know this specific
detail. The second is ordinary general knowledge, the agent answers
directly, the same "choosing not to use a tool" behavior from Lesson
15. Run the lesson and you'll see both outcomes: an exact, correct
answer pulled from the notes for the first, and a direct answer with no
tool call for the second.

## What this actually demonstrates

This is RAG (Retrieval-Augmented Generation), in full, wired into an
agent: the model can answer questions using information it was never
trained on (your own personal notes), by retrieving just the relevant
pieces instead of needing the entire document stuffed into every
request. Combined with everything else in this course so far, tool
calling, memory, context management, this is a genuinely production-
shaped pattern: an agent that knows both general knowledge and your own
private documents, and decides for itself which one a given question
needs.

## Running it

```bash
uv run python lessons/langchain/03_advanced/29_rag_as_a_tool/lesson.py
```

## Checkpoint

- **RAG as a tool**: wrapping similarity search (Lesson 28) as an
  `@tool`, so an agent decides when to search, instead of you searching
  manually every time.
- **the docstring matters even more here**: it's the only signal the
  agent has for distinguishing "search my notes" questions from general
  knowledge questions.
- **RAG's real value**: answering from documents the model never
  trained on, by retrieving only what's relevant instead of sending
  everything.

If anything here still feels unclear, ask before moving to Lesson 30.
