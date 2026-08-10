# Lesson 10: Structured output

## Free text vs a validated object

Every QueryEngine so far (Lesson 5, 01_beginner) hands back a `Response`
whose `.response` is a plain string, the LLM's synthesized answer in its
own words. That's fine for a human reading it, but brittle for a program:
if you need `max_days` as an `int` to feed into a conditional, you'd have
to regex it out of a sentence.

LlamaIndex's `output_cls` parameter fixes this by asking the LLM to fill
in a Pydantic model's fields instead of writing free text, then validating
the result against that model before returning it. A malformed or missing
field raises instead of silently handing you a broken string to parse.

| | Free-text QueryEngine | `output_cls`-constrained QueryEngine |
|---|---|---|
| `.response` type | `str` | An instance of your Pydantic model |
| Shape guaranteed? | No, whatever the LLM wrote | Yes, validated against the model |
| Good for | A human reading the answer | Feeding the answer into more code |
| LangChain equivalent | `model.invoke(prompt)` | `model.with_structured_output(Schema)` |

## Two ways to get structured output

This lesson shows both, verified against this repo's installed
`llama-index-core` (0.14.23):

1. **`index.as_query_engine(output_cls=SomeModel)`**, RAG plus structure:
   retrieve relevant Nodes, then synthesize an answer shaped like
   `SomeModel` instead of a sentence.
2. **`Settings.llm.as_structured_llm(SomeModel)`**, structure with no
   index or retrieval: wrap the LLM directly when you already have the
   text and just want it coerced into a schema.

Both routes go through the same underlying mechanism, LlamaIndex builds a
JSON-schema-constrained prompt from your Pydantic model and validates the
LLM's response against it with Pydantic itself.

## The code, piece by piece

```python
class PolicySummary(BaseModel):
    topic: str = Field(description="What policy this summary is about, in a few words")
    max_days: int = Field(description="The maximum number of days mentioned in the policy, as an integer")
    summary: str = Field(description="A one-sentence plain-English summary of the policy")
```

A plain Pydantic model describing the *shape of the answer*, not the
question. Field `description`s matter here, they get included in the
schema the LLM is asked to fill in, so a clear description is doing real
prompting work, not just documentation.

```python
query_engine = index.as_query_engine(output_cls=PolicySummary)
response = query_engine.query("Summarize the vacation policy's carryover rule...")
```

Same `as_query_engine()` call as Lesson 5, plus one new keyword. Retrieval
still happens exactly as before, only the response synthesis step changes
shape.

```python
parsed: PolicySummary = response.response
print(parsed.max_days)
```

`response.response` is now a `PolicySummary` instance, not a string.
Normal attribute access, normal types, no string-parsing.

```python
structured_llm = Settings.llm.as_structured_llm(PolicySummary)
direct = structured_llm.complete("Vacation policy: employees carry over at most 5 unused vacation days...")
direct_parsed: PolicySummary = direct.raw
```

The index-free route. `.complete()` returns a `CompletionResponse` whose
`.raw` attribute holds the parsed Pydantic object, useful when you already
have the source text in hand (e.g. from your own retrieval, or a paragraph
pasted into the prompt) and only need the schema-coercion part.

## Running it

```bash
uv run python lessons/llamaindex/02_intermediate/10_structured_output/lesson.py
```

## Expected output

The exact wording of `summary` (and possibly `max_days`, since the source
policy text mentions more than one number) varies between runs, this is
one real captured run. The types and overall shape are stable:

```
Response type: PolicySummary

Parsed PolicySummary:
  topic:   Vacation carryover rule
  max_days: 10
  summary: Unused vacation days roll over into the next year up to a maximum carryover cap of 10 days, after which anything beyond that limit is forfeited on January 1st.

max_days is a int: usable directly, e.g. in an if-statement.

Direct as_structured_llm() call (no index, no retrieval):
  topic:   Vacation carry over
  max_days: 5
  summary: Employees are allowed to carry over a maximum of 5 unused vacation days into the next calendar year.
```

Note the two `max_days` values differ (10 vs 5): the query-engine route
retrieved and summarized the *whole* vacation policy document, which
mentions a 10-day carryover cap elsewhere, while the direct
`as_structured_llm()` call was only given the one sentence about the
5-day carryover rule. Structured output constrains the *shape* of the
answer, not which facts the model chooses to surface, that's still a
retrieval and prompting question, same as with free text.

## Checkpoint

- **`output_cls`**: pass a Pydantic model to `as_query_engine()` (or
  `as_structured_llm()` on an LLM directly) to get a validated object back
  instead of free text.
- `index.as_query_engine(output_cls=Model)` combines retrieval with
  structured synthesis, RAG plus a schema.
- `Settings.llm.as_structured_llm(Model)` skips retrieval entirely, useful
  when you already have the source text.
- Field `description`s in your Pydantic model are part of the prompt, not
  just documentation, write them for the LLM as much as for future
  readers of your code.
- Structured output guarantees *shape*, not which facts get included,
  that's still governed by retrieval and the source text given to the
  model.

If anything here still feels unclear, ask before moving to Lesson 11.
