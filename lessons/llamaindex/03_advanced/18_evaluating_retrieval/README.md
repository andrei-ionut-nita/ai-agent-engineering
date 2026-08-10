# Lesson 18: Evaluating Retrieval

## Trust, but verify

Every RAG lesson up to this point has trusted the QueryEngine: retrieve
some Nodes, ask the LLM to synthesize an answer, print it, done. Nothing
checked whether that answer was actually any good. `llama_index.core.evaluation`
is a small toolkit of LLM-as-judge evaluators built for exactly that
gap, automated checks you can run against a RAG pipeline the same way
you'd run unit tests against ordinary code.

This lesson uses two of them, asking two genuinely different questions
about the same query/response/retrieved-context triple:

| Evaluator | Question it asks | Fails when |
|---|---|---|
| `FaithfulnessEvaluator` | Is the answer supported by the retrieved context? | The LLM hallucinated, answering from general knowledge instead of the documents |
| `RelevancyEvaluator` | Do the retrieved context and response actually address the query? | Retrieval fetched the wrong Nodes, even if the LLM's wording sounds fine |

A RAG pipeline can fail either check independently: retrieval can pull
the right Nodes but the LLM still invents an unsupported detail
(faithfulness fails, relevancy might still pass), or retrieval can miss
entirely and the LLM answers from its own training data instead
(faithfulness might still pass on that fabricated answer, relevancy
fails because the context doesn't address the query).

## Both evaluators are themselves LLM calls

`FaithfulnessEvaluator` and `RelevancyEvaluator` default to
`Settings.llm` as the judge if no `llm=` is passed in, same one-LLM,
multiple-jobs pattern used everywhere else in this course. This means
every evaluation costs at least one extra LLM call on top of the
query itself, worth knowing before running this against a large batch
of test questions in a real project.

## The code, piece by piece

```python
faithfulness_evaluator = FaithfulnessEvaluator()
relevancy_evaluator = RelevancyEvaluator()
```

Both default to `Settings.llm` as judge. You can pass a different,
often cheaper or more capable, `llm=` explicitly if you want the judge
to be a different model than the one answering questions.

```python
response = query_engine.query(question)
faithfulness_result = faithfulness_evaluator.evaluate_response(query=question, response=response)
```

`evaluate_response()` takes the query string and the QueryEngine's own
`Response` object directly, it pulls the retrieved context straight off
`response.source_nodes` internally, no need to pass contexts by hand.

```python
faithfulness_result.passing  # bool
faithfulness_result.score    # float, 1.0 or 0.0 for these two evaluators
```

`EvaluationResult` carries `.passing` (a bool) and `.score` (a float).
For `FaithfulnessEvaluator` and `RelevancyEvaluator` specifically, the
underlying judge is a binary YES/NO prompt, so score is always 1.0 or
0.0, other evaluators in this module (e.g. `CorrectnessEvaluator`,
not used here) return a continuous score instead.

## Running it

```bash
uv run python lessons/llamaindex/03_advanced/18_evaluating_retrieval/lesson.py
```

## Expected output

The LLM's answer wording and the evaluators' judgments can vary between
runs (both are LLM calls); captured from a real run below. In this run
both questions passed both checks, but a genuinely unanswerable question
(not tested here to conserve quota) would be expected to fail faithfulness
if the LLM speculated anyway, or fail relevancy if retrieval came up empty:

```
Q: How many vacation days can a new hire use in their first 90 days?
A: A new hire can use no more than 5 vacation days during their first 90 days of employment.

  Faithfulness: PASS (score=1.0)
  Relevancy:    PASS (score=1.0)

Q: What is the reimbursement limit for a hotel stay?
A: Based on the provided information, there is no mention of a reimbursement limit for a hotel stay. However, the policy states that travel for client visits or conferences should be booked directly through the company travel portal so it is billed to Nimbus Robotics rather than reimbursed afterward.

  Faithfulness: PASS (score=1.0)
  Relevancy:    PASS (score=1.0)
```

Note the second answer: the expense policy fixture data doesn't actually
specify a hotel limit, and the LLM correctly said so instead of making
one up, which is exactly the behavior `FaithfulnessEvaluator` is
designed to catch if it ever went the other way.

## Checkpoint

- **`FaithfulnessEvaluator`**: checks whether a response is supported by
  its retrieved context, catches hallucination.
- **`RelevancyEvaluator`**: checks whether retrieved context and response
  actually address the query, catches bad retrieval.
- Both default to `Settings.llm` as judge, and each evaluation is itself
  an extra LLM call, budget for that in larger test suites.
- `evaluate_response(query=..., response=response)` reads context
  straight off a QueryEngine's `Response` object, no manual wiring.
- `EvaluationResult.passing` (bool) and `.score` (float, 1.0/0.0 for
  these two evaluators) are the two fields to check.

If anything here still feels unclear, ask before moving to Lesson 19.
