# Lesson 24 (Capstone): Multi-Document Agentic RAG With Structured Output

## Everything this course built, in one script

This is the last lesson in the course, and it doesn't introduce a new
concept so much as wire together concepts from all three tiers:

| From | Used here as |
|---|---|
| Lesson 3, `Settings` | Global LLM/embedding config, set once |
| Lessons 4-5, `VectorStoreIndex` + `QueryEngine` | Built twice, once per document set |
| Lesson 10, `output_cls` | Applied at the agent level, not just one query engine |
| Lesson 14, tools | `QueryEngineTool.from_defaults()`, wrapping a query engine as a callable tool |
| Lessons 15-17, agents | `FunctionAgent`, reasoning over which tool(s) a question needs |

## Two document sets, one agent that picks

The Nimbus policy documents (vacation, remote work, expense) and the
Nimbus engineering documentation (engineering handbook + Cobalt-1
product FAQ, reused from `02_intermediate/13_multi_document_indexes/data/`)
are genuinely different domains, HR questions and engineering questions
shouldn't search the same index. Each gets its own small
`VectorStoreIndex`, wrapped as its own `QueryEngineTool` with a
description telling the agent what it's for:

```python
policy_tool = build_query_engine_tool(POLICY_DATA_DIR, name="hr_policies", description="...")
engineering_tool = build_query_engine_tool(ENGINEERING_DATA_DIR, name="engineering_docs", description="...")
```

`FunctionAgent` receives both tools and decides, per question, whether
it needs one, the other, or both, the same tool-selection reasoning
Lesson 14's `predict_and_call()` did for a single tool, now scaled to
multiple tools and (if needed) multiple calls in sequence.

## Structured output at the agent level

Lesson 10 showed `output_cls` on a single query engine, coercing one
synthesized answer into a Pydantic model. `FunctionAgent` accepts the
same `output_cls` keyword, applied to its *final* answer, after however
many tool calls it took to get there:

```python
class NimbusAnswer(BaseModel):
    answer: str
    document_sets_used: list[str]
    needs_human_followup: bool

agent = FunctionAgent(tools=[...], llm=Settings.llm, output_cls=NimbusAnswer, ...)
```

`document_sets_used` and `needs_human_followup` aren't things a plain
text answer would reliably self-report, having the schema force those
fields is what makes them dependable to consume downstream (log which
tools fired, route flagged answers to a human) rather than something
you'd have to regex out of prose.

## The code, piece by piece

```python
result = await agent.run(question)
```

`FunctionAgent.run()` is async (it's a `Workflow` under the hood, Lesson
19's mechanics), so this lesson wraps it in a small `run_all()`
coroutine and calls `asyncio.run()` once at the bottom, rather than
sprinkling `await` through a sync `main()`.

```python
parsed: NimbusAnswer = result.get_pydantic_model(NimbusAnswer)
```

`agent.run()` returns an `AgentOutput` event, not the Pydantic model
directly. `.get_pydantic_model(NimbusAnswer)` validates
`AgentOutput.structured_response` against the model class and returns a
real `NimbusAnswer` instance, or `None` with a warning if validation
failed, the same "coerced and validated, not just text" guarantee
Lesson 10 established.

```python
def build_query_engine_tool(data_dir, name, description) -> QueryEngineTool:
    ...
    return QueryEngineTool.from_defaults(query_engine=query_engine, name=name, description=description)
```

Factored into a function since this lesson needs the same
build-index-then-wrap-as-tool steps twice, once per document set,
identical to what Lesson 14 did for a single `FunctionTool`, just built
from a `QueryEngine` instead of a plain Python function.

## Running it

```bash
uv run python lessons/llamaindex/03_advanced/24_advanced_capstone_project/lesson.py
```

## Expected output

The agent's exact answer wording and its self-reported
`needs_human_followup` judgment can vary between runs (both are LLM
outputs); `document_sets_used` should reliably include both tool names
for this two-part question since it genuinely needs both document sets.
Captured from a real run:

```
Q: How many vacation days can a new hire use in their first 90 days, and how long does the Cobalt-1's battery last?

answer: A new hire can use a maximum of 5 vacation days during their first 90 days of employment. A fully charged Cobalt-1 battery lasts for approximately 8 hours of continuous picking work.
document_sets_used: ['hr_policies', 'engineering_docs']
needs_human_followup: False

This is the last lesson in this course.
Every piece used above, Settings, VectorStoreIndex, QueryEngine, QueryEngineTool, FunctionAgent, and structured output, was built up one lesson at a time across all three tiers.
```

The single question deliberately spans both document sets (a vacation
policy detail and a Cobalt-1 spec) so the printed `document_sets_used`
actually demonstrates the agent choosing both tools, not just
defaulting to one.

## Checkpoint

- **`QueryEngineTool.from_defaults()`**: wraps a `QueryEngine` as a tool,
  same idea as Lesson 14's `FunctionTool`, built from an index instead
  of a plain function.
- **`FunctionAgent(tools=[...], output_cls=...)`**: an agent that
  reasons over multiple tools across multiple document sets and returns
  a validated Pydantic object as its final answer, combining Lessons
  10, 14, and 15-17 into one agent.
- **`agent.run()` returns an `AgentOutput`**; call
  `.get_pydantic_model(YourModel)` to get the validated structured
  result out of it.
- Multi-document agentic RAG means giving an agent several
  narrowly-scoped retrieval tools and trusting it to pick the right
  one(s), rather than dumping every document into one big index and
  hoping retrieval alone sorts it out.

This is the last lesson in this course. Across 24 lessons you went from
"what is a Document" to a multi-tool agent that searches across several
document sets and hands back validated, structured answers, the same
ingest -> index -> query loop from Lesson 1, now with evaluation,
custom workflows, reranking, persistence, observability, and
interoperability with the wider agent ecosystem layered on top.
Congratulations on finishing the course.
