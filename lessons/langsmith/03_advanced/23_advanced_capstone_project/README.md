# Lesson 23: Advanced Capstone - Fully Instrumented Agent

## What this is

No new concepts in this lesson. This is the capstone: the calculator/
word-counter LangGraph agent, a dataset, an evaluator, a regression
gate, and a production feedback loop, everything this course covered,
combined into one script that mirrors what a real, observable LLM
application actually looks like end to end. If you can read `lesson.py`
and explain why every piece is there, you've completed this course.

## What it does

1. Creates (or reuses) a dataset of arithmetic/word-counting questions
   with known answers.
2. Runs the agent over that dataset as an experiment, scoring each
   answer and the experiment as a whole.
3. Checks the aggregate score against a baseline, failing the script
   (as CI would fail a build) if it regressed.
4. Simulates one live production request, tagged and labeled as such,
   with a user feedback score attached afterward.

## Where each piece came from

```python
builder = StateGraph(MessagesState)
...
app = builder.compile()
```
langgraph course, lesson 23, and this course's Lesson 6: the agent
itself, unchanged.

```python
DATASET_NAME = "langsmith-course-agent-qa"
EXAMPLES = [...]

def ensure_dataset() -> None:
    if client.has_dataset(dataset_name=DATASET_NAME):
        return
    ...
```
Lesson 8: a dataset built specifically for this app (question/answer
pairs the agent should get exactly right, since arithmetic and word
counts have one correct answer, unlike the RAG app's free-text
answers).

```python
def target(inputs: dict) -> dict:
    result = app.invoke({"messages": [HumanMessage(inputs["question"])]}, config={...})
    return {"answer": result["messages"][-1].text}
```
Lesson 9's `target()` shape, wrapping the agent instead of a single
function, plus Lesson 6's tagging/metadata pattern on the `config`.

```python
def answer_contains_reference(inputs, outputs, reference_outputs) -> dict: ...
def pass_rate(runs, examples) -> dict: ...
```
Lessons 10 and 11: a per-example evaluator and a summary evaluator,
here checking whether the agent's final answer contains the expected
number, individually and in aggregate.

```python
def check_for_regression(experiment_name: str) -> None:
    project = client.read_project(project_name=experiment_name)
    summary_feedback = list(client.list_feedback(sessions=[str(project.id)], feedback_key=["pass_rate"]))
    score = summary_feedback[0].score
    if score < BASELINE_PASS_RATE:
        sys.exit(1)
```
Lesson 20: reading the experiment's aggregate score back and failing
the script if it falls below an agreed baseline.

```python
def simulate_production_traffic_and_feedback() -> None:
    run_id = str(uuid.uuid4())
    result = app.invoke(..., config={"tags": [..., "production"], "metadata": {"user_id": ..., "environment": "production"}, "run_id": run_id})
    client.create_feedback(run_id=run_id, key="user_thumbs_up", score=1)
```
Lessons 17 and 21: a pre-assigned run id, production-labeling metadata,
and feedback attached after the fact, the same pattern applied one more
time to close the loop from "built and traced" (Beginner) through
"evaluated against a dataset" (Intermediate) to "monitored in
production" (Advanced).

## Running it

```bash
uv run python lessons/langsmith/03_advanced/23_advanced_capstone_project/lesson.py
```

You should see the experiment's `pass_rate` printed against its
baseline, a "No regression" message (unless the agent is genuinely
getting questions wrong), a simulated production answer, and
confirmation that feedback was published on it. In the UI: the dataset
under Datasets, the experiment under it with per-example and summary
scores, and the production run with its `user_thumbs_up` feedback and
`production`/`capstone` tags.

## Try this yourself

Without looking anything up:

- Add a fourth example the agent is likely to get wrong (say, a
  multi-step question combining both tools), does `pass_rate` drop, and
  does the regression check still correctly compare against the
  baseline?
- Lower `BASELINE_PASS_RATE` to `0.0` and re-run, confirm the script no
  longer exits non-zero even with a failing example present.
- Add a second simulated production request from a different
  `user_id`, then filter for it in the UI the way Lesson 18 did.

If you can make these changes confidently, you've completed the
langchain, langgraph, and langsmith courses. From here, the real test is
building something of your own, and watching it in LangSmith the whole
way.
