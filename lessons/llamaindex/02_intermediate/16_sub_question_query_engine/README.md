# Lesson 16: SubQuestionQueryEngine

## One index can't answer a question about data it doesn't hold

Every `QueryEngine` this course has built so far sat on top of one index
covering all the documents it needed. That breaks down once a question
spans data that's better kept in separate indexes, a vacation-policy index
has no way to answer a question about expense thresholds, and stuffing
every document into one shared index loses the benefit of describing each
one precisely for retrieval or routing.

`SubQuestionQueryEngine` solves this by adding a layer above multiple
query engines: given a compound question, it asks the LLM to break it into
sub-questions, routes each sub-question to whichever underlying
`QueryEngineTool`'s description best matches it, runs them, and
synthesizes one final answer from all the sub-answers. This is the query
engine analog of what Lesson 15's agent does with tools, decide which of
several options fits, except here the "options" are query engines and the
decision happens once, up front, rather than in an iterative loop.

| | LangChain | LlamaIndex |
|---|---|---|
| Route a compound question across sources | Custom graph/chain logic | `SubQuestionQueryEngine` |
| Each source described as | A retriever/tool with a description | A `QueryEngineTool` with a name + description |
| Splitting step | Not built in, hand-rolled | `question_gen` (an LLM call that returns sub-questions) |
| Synthesis step | Not built in, hand-rolled | A `response_synthesizer`, combines all sub-answers |

## The code, piece by piece

```python
def build_query_engine_tool(filename, name, description):
    documents = SimpleDirectoryReader(input_files=[str(DATA_DIR / filename)]).load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    return QueryEngineTool(query_engine=query_engine, metadata=ToolMetadata(name=name, description=description))
```

Builds one small, single-document `VectorStoreIndex` per policy file, the
same `from_documents()` + `as_query_engine()` pattern as Lessons 4-5, then
wraps each resulting query engine as a `QueryEngineTool`. The
`description` matters here as much as the underlying data: it's the only
thing the sub-question generator reads to decide which sub-question goes
to which tool, a vague description leads to sub-questions being routed to
the wrong tool.

```python
question_gen = LLMQuestionGenerator.from_defaults(llm=Settings.llm)
```

`SubQuestionQueryEngine.from_defaults()` normally tries to build an
OpenAI-function-calling-based question generator by default, which needs
the separate `llama-index-question-gen-openai` package, not installed in
this project, and raises `ImportError` if left to its default.
`LLMQuestionGenerator` is the provider-agnostic fallback: it prompts
`Settings.llm` directly, using structured-output parsing rather than
function calling, to produce the list of sub-questions, so it works with
any LLM, Gemini included. Passing it explicitly sidesteps the ImportError.

```python
sub_question_engine = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=[vacation_tool, expense_tool],
    question_gen=question_gen,
    use_async=False,
    verbose=True,
)
```

Assembles the engine from both tools. `verbose=True` prints each generated
sub-question, which tool it was routed to, and that sub-question's answer,
before the final synthesis step. `use_async=False` runs the sub-questions
one at a time rather than concurrently, simpler output ordering for a
lesson, at the cost of a little wall-clock time; production code would
typically leave this `True`.

```python
response = sub_question_engine.query(question)
```

Same `.query()` call shape as any other `QueryEngine` from Lesson 5
onward, the multi-index routing happens entirely inside this one call.

## Running it

```bash
uv run python lessons/llamaindex/02_intermediate/16_sub_question_query_engine/lesson.py
```

## Expected output

Captured from a real run. The sub-questions' exact wording and the final
synthesis can vary slightly between runs (both are LLM-generated), but the
routing (vacation question to `vacation_policy`, expense question to
`expense_policy`) should be stable given these tool descriptions:

```
Generated 2 sub questions.
[vacation_policy] Q: How many vacation days do new hires get access to during their first 90 days?
[vacation_policy] A: New hires cannot use more than 5 vacation days during their first 90 days of employment.
[expense_policy] Q: What is the expense reimbursement threshold that doesn't require pre-approval?
[expense_policy] A: The threshold for business expenses that can be submitted directly through the finance portal without pre-approval is under 100 EUR.

Question: How many vacation days do new hires get access to during their first 90 days, and what is the expense reimbursement threshold that doesn't require pre-approval?

Final synthesized answer:
  During their first 90 days of employment, new hires can use up to 5 vacation days. The threshold for business expenses that can be submitted directly through the finance portal without pre-approval is under 100 EUR.
```

(The real terminal output is color-coded per sub-question via ANSI escape
codes, not visible in this plain-text capture.)

## Checkpoint

- **`SubQuestionQueryEngine`**: breaks a compound question into
  sub-questions, routes each to the best-matching `QueryEngineTool`, and
  synthesizes one final answer from all the sub-answers.
- Each underlying query engine is wrapped as a `QueryEngineTool` with a
  `name` and `description`, the description drives routing, so it must be
  specific.
- `question_gen` defaults to an OpenAI-function-calling generator that
  isn't installed here, pass `LLMQuestionGenerator.from_defaults(llm=Settings.llm)`
  explicitly to use a provider-agnostic one instead.
- `verbose=True` shows the intermediate sub-questions and sub-answers, not
  just the final synthesized response.

If anything here still feels unclear, ask before moving to Lesson 17.
