# Lesson 14: The prompt engineering lifecycle, iterate, re-run, compare

## What we're building

The full loop, in one script: run an experiment against a deliberately
naive first-draft prompt, spot its weakness, push a fixed prompt to the
hub, pull it back, and re-run the identical experiment. Two
experiments, `rag-lifecycle-v1` and `rag-lifecycle-v2`, same dataset and
evaluator, different prompt.

## What this reveals

Lessons 9-12 each ran one experiment in isolation. Lesson 13 introduced
the Prompt Hub, but only round-tripped one version. Real prompt work is
a loop: notice a weakness in the current prompt's scores, change the
wording, re-run the same evaluation, see if it actually helped, repeat.
This lesson makes that loop concrete with a mistake that's genuinely
common when building a first RAG prompt: `naive_prompt` never
references `{context}` at all, so the model answers each question from
whatever it already knows, completely ignoring what `retrieve()` found.
`make_target()` still fetches context and passes it into `invoke()`,
exactly as with the working prompt, but a template with no `{context}`
placeholder simply never uses it, the same failure mode as a real app
that wired up retrieval and then forgot to actually put it in the
prompt.

Because `keyword_overlap` (Lesson 10) and the dataset (Lesson 8) stay
fixed across both runs, the prompt is the only variable, so the score
difference between v1 and v2 is attributable to the wording change, not
to a different test. Unlike a subtler wording tweak, this particular
before/after is deliberately dramatic and reliable: v1 scores
noticeably lower every time this lesson runs, since answering without
context genuinely produces different wording than the dataset's
reference answers, not just occasionally.

`make_target()` exists so that swapping which prompt is used doesn't
require duplicating the evaluation code, one function builds a `target`
closure around whatever prompt it's given, called twice with two
different prompts.

## The code, piece by piece

```python
naive_prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer in one short sentence."),
    ("human", "Question: {question}"),
])
baseline = evaluate(make_target(naive_prompt), data=DATASET_NAME, evaluators=[keyword_overlap], experiment_prefix="rag-lifecycle-v1")
```

The bug: no `{context}` placeholder anywhere in this prompt, so
retrieval happens (inside `make_target`) but its result is thrown away.
Same `evaluate()` call as Lesson 10 otherwise.

```python
grounded_prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer using only the given context, in one short sentence."),
    ("human", "Context:\n{context}\n\nQuestion: {question}"),
])
client.push_prompt(PROMPT_NAME, object=grounded_prompt)
```

The fix: a `{context}` placeholder, and an instruction to actually use
it. This is the same prompt pushed in Lesson 13, pushed again here so
this lesson is runnable on its own without depending on Lesson 13
having already run. Pushing under the same `PROMPT_NAME` creates a new
version rather than a new prompt.

```python
v2_prompt = client.pull_prompt(PROMPT_NAME)
v2 = evaluate(make_target(v2_prompt), ..., experiment_prefix="rag-lifecycle-v2")
```

Pulling again (rather than reusing the local `grounded_prompt` variable)
proves the loop works the way it would in a real team: someone else
could have made this edit directly in the hub's UI, and pulling is how
your evaluation code picks it up.

## Running it

```bash
uv run python lessons/langsmith/02_intermediate/14_prompt_engineering_lifecycle/lesson.py
```

In the UI, compare `rag-lifecycle-v1` and `rag-lifecycle-v2`'s
`keyword_overlap` scores side by side, v2 should score meaningfully
higher, and check the Prompt Hub entry for `langsmith-course-rag-prompt`
to see both versions listed. In one real run of this lesson, v1 averaged
`0.38` and v2 averaged `0.64`, your numbers won't match exactly (Gemini's
wording varies run to run), but the gap should be consistently large.

## Checkpoint

- **The lifecycle**: run an experiment, spot a weakness, edit the
  prompt, push it, pull it again, re-evaluate, compare, repeat.
- **Keeping everything else fixed**: reusing the same dataset and
  evaluator across both runs is what makes the score difference
  attributable to the prompt change specifically.
- **A missing `{context}` placeholder is a silent bug**: the retrieved
  text can be fetched and available and still never reach the model, if
  the prompt template simply doesn't reference it, evaluation is what
  catches this, not a stack trace.
- **Prompt versions accumulate**: each `push_prompt` call to the same
  name is a new, inspectable version, not an overwrite.

If anything here still feels unclear, ask before moving to Lesson 15.
