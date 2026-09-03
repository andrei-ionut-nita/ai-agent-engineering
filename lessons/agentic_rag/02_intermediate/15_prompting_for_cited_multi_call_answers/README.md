# Lesson 15: Prompting for Cited, Multi-Call Answers

## Where we left off

[naive_rag Lesson 15](../../../naive_rag/02_intermediate/15_prompting_for_grounded_answers/README.md)
already taught citing a single retrieval's source. This lesson's twist
is specific to the agentic case: when an answer draws on *two separate*
`search_notes()` calls, each returning a different document, a naive
citation instruction ("cite your source") tends to produce one citation
covering an answer that actually needs two, silently implying the
second fact came from the same place as the first.

## The code, piece by piece

```python
SYSTEM_INSTRUCTION = """... When you give your final answer, cite the
source file ... each fact came from, right after that fact. If you
used more than one source, every fact needs its own citation, don't
cite only the first one and assume it covers the rest."""
```

The last sentence is doing the real work here, and it exists because
of a failure mode you can reproduce by removing it: with a plain
"cite your sources" instruction, a model synthesizing two retrieved
facts into one fluent paragraph will often cite only once, typically
at the end, in a way that reads as covering the whole answer even
though only the last fact actually came from that source.

```python
return "\n\n---\n\n".join(f"[{r['source']}]\n{r['text']}" for r in top_k)
```

Unchanged from Lesson 10, included here as a reminder: citation is only
possible because `search_notes()` already tags every passage with its
source filename. A tool result with no source information gives the
model nothing to cite, no matter how the prompt is worded.

## Running it

```bash
uv run python lessons/agentic_rag/02_intermediate/15_prompting_for_cited_multi_call_answers/lesson.py
```

## Expected output

```
Q: How often should the aquarium's filter sponge be rinsed, and how often does the sourdough starter need feeding at room temperature?

A: The aquarium's filter sponge should be rinsed every other water change [home-aquarium.md]. Separately, the sourdough starter needs feeding every 12 hours at room temperature [sourdough-starter.md].
```

Two distinct `[source.md]` tags, one per fact, is the thing to check
for, not just that citations exist somewhere in the answer.

## Checkpoint

- Multi-call answers need a citation instruction that explicitly
  addresses combining facts from more than one source, a single-source
  citation instruction tends to under-cite once more than one document
  is involved.
- `search_notes()`'s `[source.md]` tags are what make citation possible
  at all, the instruction only shapes what the model does with
  information it already has access to.
- **Try this yourself**: delete the sentence "If you used more than
  one source, every fact needs its own citation..." from
  `SYSTEM_INSTRUCTION` and rerun. Does the answer still cite both
  sources, or does it drop one?

If anything here still feels unclear, ask before moving to Lesson 16.
