# Lesson 22: External Web Search as the "Incorrect" Branch

## Where we left off, and what this lesson actually is

Read this one carefully: **this lesson, not Lessons 6-7, is what
"Corrective RAG" means in Yan et al. 2024.** Lesson 1 named the internal
rewrite-and-re-retrieve loop as a deliberate simplification, easier to
build first, but not the paper's real mechanism. The paper's actual
response to a low-confidence grade is external web search, a genuinely
different knowledge source, not another attempt against the same
corpus. This lesson builds that real branch.

## Why this distinction matters

An internal rewrite (Lessons 6-7) can only ever find what's already in
the corpus, worded differently. If the corpus never had the answer, no
number of rewrites changes that, Lesson 21's bounded loop makes this
failure honest, but it doesn't make it succeed. External search can
succeed where internal rewriting structurally cannot: it reaches
information the corpus never contained at all. That's the actual gap
this course named in Lesson 1 and has been carrying since.

## Pluggable, stubbed, no required external API key

```python
_MOCK_WEB_INDEX = {
    "capital of france": "Paris is the capital and most populous city of France.",
}

def mock_web_search(query: str) -> str | None:
    ...

ExternalSearch = Callable[[str], "str | None"]
```

This course only requires `GOOGLE_API_KEY`, so this lesson mocks the
external search with a tiny hardcoded index instead of calling a real
search API. What matters is the **shape** of the interface: a function
that takes a query string and returns matched text or `None`. A real
provider (Tavily, Bing, Google Programmable Search, whatever's
available in a given deployment) plugs into that exact same shape, no
other code in this file changes.

```python
def corrective_ask_with_external_fallback(
    query: str,
    store: list[dict],
    external_search: ExternalSearch,
    k: int = 3,
) -> str:
```

`external_search` is passed in as a parameter, not hardcoded, this is
what "pluggable" means concretely: the caller decides which
implementation to use, `mock_web_search` here, a real API client in a
production system, without `corrective_ask_with_external_fallback`
itself needing to know or care which.

## The code, piece by piece

```python
if relevant:
    context = "\n\n---\n\n".join(c["text"] for c in relevant)
    source_note = "the notes collection"
else:
    web_result = external_search(query)
    if web_result is None:
        return "I don't have any information relevant to that question, internally or externally."
    context = web_result
    source_note = "external web search"
```

The real branch: internal retrieval first, exactly as before, but the
"nothing relevant" case (Lessons 6-7's rewrite trigger) now falls
through to `external_search()` instead of rephrasing the same question
against the same five files.

## Running it

```bash
uv run python lessons/corrective_rag/03_advanced/22_external_web_search_as_the_incorrect_branch/lesson.py
```

## Expected output

```
Q: How often does the wind speed sensor need re-oiling?
A: Based on the notes collection (Project Aurora), the wind speed sensor needs re-oiling every few months.

Q: What is the capital of France?
A: Based on the provided context (which came from an external web search): The capital of France is Paris.

The first question resolves entirely from the internal corpus, ...
```

The France question, unanswerable by every previous lesson in this
course, finally gets a real answer, not because the internal corpus
changed, but because this lesson finally builds the branch that reaches
outside it.

## Checkpoint

- **This is the paper's real "incorrect" branch.** Lessons 6-7's
  internal rewrite was a named simplification (Lesson 1), useful for
  wording problems, structurally incapable of finding information the
  corpus never had.
- **Pluggable interface**: `Callable[[str], str | None]`, a query in,
  matched text or nothing out. Any real search provider fits this shape
  without changing the calling code.
- No external API key is required to run this course, the mock index
  demonstrates the mechanism honestly, at the cost of only knowing about
  the one query it was seeded with.

If anything here still feels unclear, ask before moving to Lesson 23.
